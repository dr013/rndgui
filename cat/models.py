# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.urls import reverse


# Create your models here.
class DBInstance(models.Model):
    host = models.CharField('Host', max_length=200)
    sid = models.CharField('SID', max_length=20, blank=True, null=True)
    port = models.IntegerField('Port', default=1521)
    login = models.CharField('Login', max_length=200)
    passwd = models.CharField('Password', max_length=200)
    dbname = models.CharField('Service', max_length=20, blank=True, null=True)
    sys_user = models.CharField('System Login', max_length=200, blank=True, null=True, default='system')
    sys_passwd = models.CharField('System Password', max_length=200, blank=True, null=True, default='SYSTEM1')
    weight = models.IntegerField('Weight')

    def __str__(self):
        return '{host}::{login}'.format(host=self.host, login=self.login)

    def get_absolute_url(self):
        return reverse('instance-detail', kwargs={'pk': self.pk})
