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
from common.jenkins_wrapper import JenkinsWrapper
from common.func import create_hash
from django.conf import settings


STATUSES = (
    ('completed', 'Completed'),
    ('busy', 'Busy'),
    ('fail', 'Failed'),
    ('abort', 'Aborted'),
    ('timeout', 'Timeout'),
)

# Get an instance of a logger
logger = logging.getLogger(__name__)


def get_next_release(product):
    #   get all releases from carousel
    """
        Get next release for testing by product
        :param product:
        :return: release for testing in string format
    """
    release = ''
    logger.info("Get Release for testing by product [{p}]".format(p=product.name))
    try:
        release = ReleaseCarousel.objects.all().filter(release__product=product).order_by('count', 'last_used_at').first()
    except ReleaseCarousel.DoesNotExist, err:
        logger.error("Release for testing not found error - {e}".format(e=err))
    if release:
        logger.info("Release for testing is [{r}]".format(r=release))
        release.use()
        return release


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
        ordering = ['name']

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
            if "busy" not in data.status:
                return 'Ready'
            else:
                return 'Busy'
        else:
            return "Ready"

    @property
    def hash(self):
        data = UsageLog.objects.all().filter(stand=self).order_by('-started_at').first()
        if data:
            if "busy" not in data.status:
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
        jenkins = JenkinsWrapper()
        #   generate unique hash code
        stand_hash = create_hash()
        #   get the last usage info about the current stand
        usage_info_arr = UsageLog.objects.all().filter(stand=self)
        #   if the stand has not previously been used
        if usage_info_arr.count() > 0:
            #   To the last record about the used stand
            last_usage_stand = usage_info_arr.order_by('-started_at')[0]
            # if the current stand in "busy" status - skip them
            if 'busy' in last_usage_stand.status:
                logger.info("Stand [{st}] - is busy".format(st=self.name))
            else:
                logger.info("Stand [{st}] - free, can use it".format(st=self.name))
                # get next release for testing by Product, if it not set in params
                if not release:
                    release = get_next_release(product=self.prd)
                    #   if releaseCarousel is empty
                    if not release:
                        logger.warning("Releases carousel is empty. There is nothing to test ")
                        return False

                #   run Jenkins task on "free" stand
                task = jenkins.run_build(task=settings.JENKINS_BUILD_TASK,
                                         param={'RELEASE': release, 'HOST': self.name, 'HASH': stand_hash})
                #   save selected stand to database, and mark as 'busy'
                use = UsageLog(stand=self,
                               release=get_object_or_404(Release, name=release),
                               status='busy',
                               task=task,
                               author=user,
                               hash=stand_hash)
                use.save()
                return self
        #   if the stand has previously been used
        else:
            logger.info("Stand [{st}] - free and it can use now".format(st=self.name))
            # get next release for testing by Product, if it not set in params
            if not release:
                release = get_next_release(product=self.prd)
                #   if releaseCarousel is empty
                if not release:
                    logger.warning("Releases carousel is empty. There is nothing to test ")
                    return False

            #   run Jenkins task on "free" stand
            task = jenkins.run_build(task=settings.JENKINS_BUILD_TASK,
                                     param={'RELEASE': release, 'HOST': self.name, 'HASH': stand_hash})
            #   save selected stand to database, and mark as 'busy'
            use = UsageLog(stand=self,
                           release=get_object_or_404(Release, name=release),
                           status='busy',
                           task=task,
                           author=user,
                           hash=stand_hash)
            use.save()
            return self
        return False


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

    def release_stand(self, status, force=False):
        """
            Method for release (unlock) 'busy' stand
            :param status: The status of the result testing on stand
            :param force: If set to 'true' Jenkins task will be aborted
            :return: self instance
        """
        #   set 'finished' time
        self.finished_at = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())
        #   if 'force' - abort Jenkins jobs
        if force:
            jenkins = JenkinsWrapper()
            jenkins.stop_build(task_url=self.task)
        self.status = status
        self.save()
        logger.info("Stand [{st}] - was released".format(st=self.stand))
        return self


class ReleaseCarousel(models.Model):
    release = models.OneToOneField(Release, unique=True)
    count = models.IntegerField('Count', null=True, blank=True, default=0)
    created_at = models.DateTimeField(verbose_name='Created', auto_now_add=True)
    last_used_at = models.DateTimeField(verbose_name='Last used')
    sort = models.IntegerField('Sort', default=10)

    class Meta:
        ordering = ['count', 'last_used_at', 'sort']

        permissions = (
            ("can_order", "Manual order priority"),
        )

    @property
    def is_first(self):
        first_rec = ReleaseCarousel.objects.all().filter().order_by('count', 'last_used_at').first()
        if self == first_rec:
            return True
        else:
            return False

    @property
    def is_last(self):
        last_rec = ReleaseCarousel.objects.all().filter().order_by('count', 'last_used_at').last()
        if self == last_rec:
            return True
        else:
            return False

    def get_absolute_url(self):
        return reverse('rcarousel-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return '{r}'.format(r=self.release.name)

    def use(self):
        self.count += 1
        self.last_used_at = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())
        self.save()
