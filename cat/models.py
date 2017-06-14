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
from binascii import hexlify
import os


STATUSES = (
    ('completed', 'Completed'),
    ('busy', 'Busy'),
    ('fail', 'Failed'),
)

# Get an instance of a logger
logger = logging.getLogger('cat')


# Create your models here.
class TestEnvironment(models.Model):
    name = models.CharField('Name', max_length=200)
    env = models.ForeignKey(Environment, verbose_name='Environment')
    prd = models.ForeignKey(Product, verbose_name='Product', null=True, blank=True)
    expire = models.CharField('Expire time', max_length=200, default=120)
    is_active = models.BooleanField("Is active", default=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('test-env-detail', kwargs={'pk': self.pk})

    @property
    def status(self):
        data = UsageLog.objects.all().filter(stand=self).order_by('-started_at')[0]
        if ("fail" in data.status) or ("completed" in data.status):
            return 'Free'
        else:
            return 'Busy'

    def acquire(self, release, user=None):
        available_stand = TestEnvironment.objects.all().filter(is_active=True)
        for stand in available_stand:
            logger.info("Check stand [{st}]:".format(st=stand.name))
            usage_info = UsageLog.objects.all().filter(stand=stand)

            if usage_info.count() > 0:
                last_usage_stand = usage_info.order_by('-started_at')[0]

                if 'busy' in last_usage_stand.status:
                    logger.info("Stand [{st}] - is busy".format(st=stand.name))
                else:
                    logger.info("Stand [{st}] - is free, can use it".format(st=stand.name))
                    # TODO add run jenkins task at selected stand, and return task name
                    task = 'CI task'
                    use = UsageLog(stand=stand, release=release, status='busy', task=task, author=user)
                    use.save()
                    break

            else:
                logger.info("Stand [{st}] - is free and it can use now".format(st=stand.name))
                # TODO add run jenkins task at selected stand, and return task name
                task = 'CI task'
                use = UsageLog(stand=stand, release=release, status='busy', task=task, author=user)
                use.save()
                break

    def auto_acquire(self, user=None):
        available_stand = TestEnvironment.objects.all().filter(is_active=True)
        for stand in available_stand:
            logger.info("Check stand [{st}]:".format(st=stand.name))
            #   TODO get Release by 'stand.product'
            release = Release.objects.get(pk=1)
            usage_info = UsageLog.objects.all().filter(stand=stand)

            if usage_info.count() > 0:
                last_usage_stand = usage_info.order_by('-started_at')[0]

                if 'busy' in last_usage_stand.status:
                    logger.info("Stand [{st}] - is busy".format(st=stand.name))
                else:
                    logger.info("Stand [{st}] - is free, can use it".format(st=stand.name))
                    # TODO add run jenkins task at selected stand, and return task name
                    task = 'CI task'
                    use = UsageLog(stand=stand, release=release, status='busy', task=task, author=user)
                    use.save()
            else:
                logger.info("Stand [{st}] - is free and it can use now".format(st=stand.name))
                # TODO add run jenkins task at selected stand, and return task name
                task = 'CI task'
                use = UsageLog(stand=stand, release=release, status='busy', task=task, author=user)
                use.save()

    def release(self, hash, status='completed'):
        try:
            usage_info = UsageLog.objects.get(hash=hash)
            usage_info.finished_at = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())
            usage_info.status = status
            usage_info.save()
            logger.info("Stand [{st}] - is released".format(st=usage_info.stand))
        except UsageLog.DoesNotExist:
            logger.error("Log record with hash [{h}] not found!".format(h=hash))

    def auto_release(self):
        usage_info = UsageLog.objects.all().filter(status='busy')
        for usage_stand in usage_info:
            start_time = datetime.datetime.strftime(usage_stand.started_at, "%H:%M:%S %d/%m")
            logger.info("Check busy's stand [{st}], started at {tm}:".format(st=usage_stand.stand,
                                                                             tm=start_time))
            stand = TestEnvironment.objects.get(name=usage_stand.stand)
            expire_data = usage_stand.started_at + datetime.timedelta(minutes=int(stand.expire))
            print_expire_date = datetime.datetime.strftime(expire_data, "%d/%m %H:%M:%S")
            if expire_data < timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone()):
                logger.info("End time [{ex}] fot stand [{st}] is over. Abort work.".format(st=stand.name,
                                                                                           ex=print_expire_date))
                usage_stand.status = 'fail'
                usage_stand.finished_at = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())
                usage_stand.save()
            else:
                logger.info("End time [{ex}] for stand [{st}] is not out. Continue.".format(st=stand.name,
                                                                                            ex=print_expire_date))


#   TODO remove this
def _create_hash():
    """This function generate 10 character long hash"""
    return hexlify(os.urandom(5))


class UsageLog(models.Model):
    stand = models.ForeignKey(TestEnvironment, verbose_name='TestEnvironment')
    release = models.ForeignKey(Release, verbose_name='Release')
    status = models.CharField('Statuses', choices=STATUSES, max_length=200, default='busy')
    started_at = models.DateTimeField(verbose_name='Start time', auto_now_add=True)
    finished_at = models.DateTimeField(verbose_name='Finish time', null=True, blank=True)
    task = models.CharField('Task', max_length=200, null=True, blank=True)
    #   TODO change call func _create_hash to common.func.create_hash
    hash = models.CharField(max_length=10, default=_create_hash, editable=False, unique=True)
    author = models.ForeignKey(User, null=True, blank=True)

    def __str__(self):
        return '{name}::{status}'.format(name=self.stand, status=self.status)
