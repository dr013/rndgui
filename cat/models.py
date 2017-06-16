# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.urls import reverse
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
)

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your models here.
class TestEnvironment(models.Model):
    name = models.CharField('Name', max_length=200, unique=True)
    env = models.ForeignKey(Environment, verbose_name='Environment')
    prd = models.ForeignKey(Product, verbose_name='Product', null=True, blank=True)
    expire = models.CharField('Expire time', max_length=200, default=120)
    is_active = models.BooleanField("Is active", default=True)

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
        acquire_stand = ''
        available_stand = TestEnvironment.objects.all().filter(is_active=True)
        for stand in available_stand:
            logger.info("Check stand [{st}]:".format(st=stand.name))

            #   TODO get Release for testing by 'stand.product'
            if not release:
                release = Release.objects.get(pk=1)

            usage_info = UsageLog.objects.all().filter(stand=stand)

            stand_hash = create_hash()

            if usage_info.count() > 0:
                last_usage_stand = usage_info.order_by('-started_at')[0]

                if 'busy' in last_usage_stand.status:
                    logger.info("Stand [{st}] - is busy".format(st=stand.name))
                else:
                    logger.info("Stand [{st}] - free, can use it".format(st=stand.name))

                    jenkins = JenkinsWrapper()
                    task = jenkins.run_build(task=settings.JENKINS_BUILD_TASK,
                                             param={'RELEASE': release.name,
                                                    'HOST': stand.name,
                                                    'HASH': stand_hash})
                    use = UsageLog(stand=stand, release=release, status='busy', task=task, author=user, hash=stand_hash)
                    use.save()
                    acquire_stand = stand
                    break
            else:
                logger.info("Stand [{st}] - free and it can use now".format(st=stand.name))
                jenkins = JenkinsWrapper()
                task = jenkins.run_build(task=settings.JENKINS_BUILD_TASK,
                                         param={'RELEASE': release.name,
                                                'HOST': stand.name,
                                                'HASH': stand_hash})
                use = UsageLog(stand=stand, release=release, status='busy', task=task, author=user, hash=stand_hash)
                use.save()
                acquire_stand = stand
                break
        return acquire_stand

    def release(self, hash, status='completed', force=False):
        result = False
        try:
            usage_info = UsageLog.objects.get(hash=hash)
            usage_info.finished_at = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())
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
        usage_info = UsageLog.objects.all().filter(status='busy')
        jenkins = JenkinsWrapper()
        for usage_stand in usage_info:
            start_time = datetime.datetime.strftime(usage_stand.started_at, "%H:%M:%S %d/%m")
            logger.info("Run check used stand [{st}], started at {tm}:".format(st=usage_stand.stand,
                                                                             tm=start_time))
            stand = TestEnvironment.objects.get(name=usage_stand.stand)
            expire_data = usage_stand.started_at + datetime.timedelta(minutes=int(stand.expire))
            print_expire_date = datetime.datetime.strftime(expire_data, "%d/%m %H:%M:%S")
            if expire_data < timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone()):
                logger.info("End time [{ex}] for stand [{st}] is over. "
                            "The work will be abort.".format(st=stand.name,
                                                             ex=print_expire_date))
                usage_stand.status = 'fail'
                usage_stand.finished_at = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())
                usage_stand.save()
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
