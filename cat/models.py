# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models import Q
from django.db import models
from django.urls import reverse
from envrnmnt.models import Environment
from prd.models import Product, Release

STATUSES = (
    ('free', 'Free'),
    ('busy', 'Busy'),
    ('disable', 'Disabled'),
)

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

    def get_fields(self):
        return [(field.verbose_name, field._get_val_from_obj(self)) for field in self.__class__._meta.fields]

    def acquire(self):
        available_stand = TestEnvironment.objects.all().filter(is_active=True)
        usage_stand = UsageLog.getFreeStand()
        for stand in available_stand:
            print stand.name

    def release(self):
        pass


class UsageLog(models.Model):
    stand = models.ForeignKey(TestEnvironment, verbose_name='TestEnvironment')
    release = models.ForeignKey(Release, verbose_name='Release')
    status = models.CharField('Statuses', choices=STATUSES, max_length=200, default='free')
    started_at = models.DateTimeField(verbose_name='Start time', auto_now_add=True, editable=False)
    finished_at = models.DateTimeField(verbose_name='Finish time', auto_now=True, editable=False)

    def getFreeStand(self):
        return self.objects.all().filter(~Q(status='free'))
