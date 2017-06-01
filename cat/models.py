# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.urls import reverse

WEIGHT_ARR = (
    ('Big', 'For SmartVista project'),
    ('Medium', 'For SMSGate, SSO projects'),
    ('Small', 'For other project'),
)


# Create your models here.
class DBInstance(models.Model):
    host = models.CharField('Host', max_length=200)
    sid = models.CharField('SID', max_length=20, blank=True, null=True, default='SV')
    port = models.IntegerField('Port', default=1521)
    login = models.CharField('Login', max_length=200)
    passwd = models.CharField('Password', max_length=200)
    sys_user = models.CharField('System Login', max_length=200, blank=True, null=True, default='system')
    sys_passwd = models.CharField('System Password', max_length=200, blank=True, null=True, default='SYSTEM1')
    weight = models.CharField('Weight', choices=WEIGHT_ARR, max_length=200,)

    def __str__(self):
        return '{host}::{login}'.format(host=self.host, login=self.login)

    def get_absolute_url(self):
        return reverse('instance-detail', kwargs={'pk': self.pk})


class WEBInstance(models.Model):
    host = models.CharField('Host', max_length=200)
    port = port = models.IntegerField('Port', default=1521)
    target_server = models.CharField('Server name', max_length=200)
    host_login = models.CharField('Server name', max_length=200)

    def __str__(self):
        return 't3://{host}:{port}'.format(host=self.host, login=self.port)

    def get_absolute_url(self):
        return reverse('instance-detail', kwargs={'pk': self.pk})


class STLNInstance(models.Model):
    host = models.CharField('Host', max_length=200)
    host_login = models.CharField('Server name', max_length=200)

    def __str__(self):
        return '{host_login}@{host}'.format(host=self.host, login=self.host_login)

    def get_absolute_url(self):
        return reverse('instance-detail', kwargs={'pk': self.pk})
