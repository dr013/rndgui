# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.urls import reverse
from django.shortcuts import get_object_or_404
from envrnmnt.models import Environment
from prd.models import Product, Release
from django.contrib.auth.models import User
import logging
import datetime
from django.utils import timezone
import requests
from common.jenkins_wrapper import JenkinsWrapper
from common.func import create_hash
from django.conf import settings


STATUSES = (
    ('completed', 'Completed'),
    ('busy', 'Busy'),
    ('fail', 'Failed'),
)

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your models here.
class TestEnvironment(models.Model):
    name = models.CharField('Name', max_length=200, unique=True)
    env = models.ForeignKey(Environment, verbose_name='Environment')
    prd = models.ForeignKey(Product, verbose_name='Product', null=True, blank=True)
    expire = models.CharField('Expire time', max_length=200, default=120)

    class Meta:
        permissions = (
            ("can_unlock", "Can force unlock stand"),
            ("can_run", "Can manual run stand"),
        )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('test-env-detail', kwargs={'pk': self.pk})

    @property
    def is_active(self):
        env = Environment.objects.all().filter(name=self.env).values('is_active')
        return env[0]['is_active']

    @property
    def status(self):
        data = UsageLog.objects.all().filter(stand=self).order_by('-started_at').first()
        if data:
            if ("fail" in data.status) or ("completed" in data.status):
                return 'Ready'
            else:
                return 'Busy'
        else:
            return "Ready"

    @property
    def hash(self):
        data = UsageLog.objects.all().filter(stand=self).order_by('-started_at').first()
        if data:
            if ("fail" in data.status) or ("completed" in data.status):
                return False
            else:
                return data.hash
        else:
            return False

    def acquire(self, user=None, release=None):
        """
            Func for acquire stand for testing
            :param user:  Save authenticated user in database
            :param release: Release for testing
            :return: Stand for testing
        """
        acquire_stand = ''
        #   generate unique hash code
        stand_hash = create_hash()
        #   TODO maybe need refactoring below code
        #   get all exists stands from the db
        all_stands = self.__class__.objects.all()
        for stand in all_stands:
            logger.info("Check stand [{st}]:".format(st=stand.name))
            #   if the stand is not active
            if stand.is_active:
                #   get the last usage info about the current stand
                usage_info_arr = UsageLog.objects.all().filter(stand=stand)
                #   if the stand has not previously been used
                if usage_info_arr.count() > 0:
                    #   To the last record about the used stand
                    last_usage_stand = usage_info_arr.order_by('-started_at')[0]
                    # if the current stand in "busy" status - skip them
                    if 'busy' in last_usage_stand.status:
                        logger.info("Stand [{st}] - is busy".format(st=stand.name))
                    else:
                        logger.info("Stand [{st}] - free, can use it".format(st=stand.name))
                        # get next release for testing by Product, if it not set in params
                        if not release:
                            release = self.get_release_for_test(stand.prd)

                        jenkins = JenkinsWrapper()
                        #   run Jenkins task on "free" stand
                        task = jenkins.run_build(task=settings.JENKINS_BUILD_TASK,
                                                 param={'RELEASE': release,
                                                        'HOST': stand.name,
                                                        'HASH': stand_hash})
                        #   save selected stand to database, and mark as 'busy'
                        use = UsageLog(stand=stand,
                                       release=get_object_or_404(Release, name=release),
                                       status='busy',
                                       task=task,
                                       author=user,
                                       hash=stand_hash)
                        use.save()
                        acquire_stand = stand
                        break
                #   if the stand has previously been used
                else:
                    logger.info("Stand [{st}] - free and it can use now".format(st=stand.name))
                    # get next release for testing by Product, if it not set in params
                    if not release:
                        release = self.get_release_for_test(stand.prd)

                    jenkins = JenkinsWrapper()
                    #   run Jenkins task on "free" stand
                    task = jenkins.run_build(task=settings.JENKINS_BUILD_TASK,
                                             param={'RELEASE': release,
                                                    'HOST': stand.name,
                                                    'HASH': stand_hash})
                    #   save selected stand to database, and mark as 'busy'
                    use = UsageLog(stand=stand,
                                   release=get_object_or_404(Release, name=release),
                                   status='busy',
                                   task=task,
                                   author=user,
                                   hash=stand_hash)
                    use.save()
                    acquire_stand = stand
                    break
            else:
                logger.info("Stand [{st}] - is disabled".format(st=stand.name))
        return acquire_stand

    #   TODO update method getting "Release for testing"
    def get_release_for_test(self, product):
        data = {}
        logger.info("Get Release for testing by product [{p}]".format(p=product.name))
        url = '{h}/r-carousel/api/get/?project=core&product={p}'.format(h=settings.SERVICE_HOST,
                                                                        p=product.name)
        try:
            response = requests.get(url=url)
            data = response.json()
        except requests.HTTPError, err:
            logger.error("HTTP error - {e}".format(e=err))
        if data:
            logger.debug(str(data))
            logger.info("Release for testing is [{r}]".format(r=data['release']))
            return data['release']

    #   TODO maybe move this method to UsageLog class
    def release(self, hash, status='completed', force=False):
        """
            Method for release (unlock) 'busy' stand
            :param hash: The security hash code for unlock specified stand, not all or any
            :param status: The status of the result testing on stand
            :param force: If set to 'true' Jenkins task will be aborted
            :return:
        """
        result = False
        try:
            #   try get 'busy' stand by set hash
            usage_info = UsageLog.objects.get(hash=hash)
            #   set 'finished' time
            usage_info.finished_at = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())
            #   if 'force' - abort Jenkins jobs
            if force:
                jenkins = JenkinsWrapper()
                jenkins.stop_build(task_url=usage_info.task)
                status = 'fail'
            usage_info.status = status
            usage_info.save()
            logger.info("Stand [{st}] - was released".format(st=usage_info.stand))
            result = usage_info.stand
        except UsageLog.DoesNotExist:
            logger.error("Log record with hash [{h}] was not found!".format(h=hash))
        return result

    def auto_release(self):
        """
            Func for autoRelease (unlock) all stand
        """
        #   get all 'busy' stands
        usage_info = UsageLog.objects.all().filter(status='busy')
        jenkins = JenkinsWrapper()
        for usage_stand in usage_info:
            #   get the stand startTime's
            start_time = datetime.datetime.strftime(usage_stand.started_at, "%H:%M:%S %d/%m")
            logger.info("Run check used stand [{st}], started at {tm}:".format(st=usage_stand.stand,
                                                                               tm=start_time))
            #   TODO maybe need refactoring below code
            #   get stand from Model by stand from UsageLog
            stand = self.__class__.objects.get(name=usage_stand.stand)
            #   get expireTime for stand
            expire_data = usage_stand.started_at + datetime.timedelta(minutes=int(stand.expire))
            #   human's expireTime
            print_expire_date = datetime.datetime.strftime(expire_data, "%d/%m %H:%M:%S")
            #   if DateTime.now() more than expireTime, unlock stand
            if expire_data < timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone()):
                logger.info("End time [{ex}] for stand [{st}] is over. "
                            "The work will be abort.".format(st=stand.name,
                                                             ex=print_expire_date))
                #   set Failed status
                usage_stand.status = 'fail'
                #   set finishTime
                usage_stand.finished_at = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())
                usage_stand.save()
                #   abort Jenkins jobs
                jenkins.stop_build(task_url=usage_stand.task)
            else:
                logger.info("End time [{ex}] for stand [{st}] is not out. Continue work.".format(st=stand.name,
                                                                                                 ex=print_expire_date))


class UsageLog(models.Model):
    stand = models.ForeignKey(TestEnvironment, verbose_name='Environment')
    release = models.ForeignKey(Release, verbose_name='Release')
    status = models.CharField('Statuses', choices=STATUSES, max_length=200, default='busy')
    started_at = models.DateTimeField(verbose_name='Start time', auto_now_add=True)
    finished_at = models.DateTimeField(verbose_name='Finish time', null=True, blank=True)
    task = models.CharField('Task', max_length=200, null=True, blank=True)
    hash = models.CharField(max_length=10, editable=False, unique=True)
    author = models.ForeignKey(User, null=True, blank=True)

    def __str__(self):
        return '{name}::{status}'.format(name=self.stand, status=self.status)
