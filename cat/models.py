# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType

WEIGHT_ARR = (
    ('Big', 'For SmartVista project'),
    ('Medium', 'For SMSGate, SSO projects'),
    ('Small', 'For other project'),
)


class DBInstance(models.Model):
    host = models.CharField('Host', max_length=200)
    sid = models.CharField('SID', max_length=20, blank=True, null=True, default='SV')
    port = models.IntegerField('Port', default=1521)
    login = models.CharField('Login', max_length=200)
    passwd = models.CharField('Password', max_length=200)
    sys_user = models.CharField('System Login', max_length=200, blank=True, null=True, default='system')
    sys_passwd = models.CharField('System Password', max_length=200, blank=True, null=True, default='SYSTEM1')
    weight = models.CharField('Weight', choices=WEIGHT_ARR, max_length=200,)
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey()

    def __str__(self):
        return '{host}::{login}'.format(host=self.host, login=self.login)

    def get_absolute_url(self):
        return reverse('dbinstance-detail', kwargs={'pk': self.pk})

    def get_fields(self):
        return [(field.verbose_name, field._get_val_from_obj(self)) for field in self.__class__._meta.fields]


class WEBInstance(models.Model):
    host = models.CharField('Host', max_length=200)
    port = models.IntegerField('Port', default=7001)
    target_server = models.CharField('Server', max_length=200)
    host_login = models.CharField('Host login', max_length=200, default='weblogic')
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey()

    def __str__(self):
        return 't3://{host}:{port}'.format(host=self.host, port=self.port)

    def get_absolute_url(self):
        return reverse('webinstance-detail', kwargs={'pk': self.pk})

    def get_fields(self):
        return [(field.verbose_name, field._get_val_from_obj(self)) for field in self.__class__._meta.fields]


class STLNInstance(models.Model):
    host = models.CharField('Host', max_length=200)
    host_login = models.CharField('Host login', max_length=200)
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey()

    def __str__(self):
        return '{host_login}@{host}'.format(host=self.host, host_login=self.host_login)

    def get_absolute_url(self):
        return reverse('stlninstance-detail', kwargs={'pk': self.pk})

    def get_fields(self):
        return [(field.verbose_name, field._get_val_from_obj(self)) for field in self.__class__._meta.fields]


class Environment(models.Model):
    name = models.CharField('Name', max_length=200)
    is_active = models.BooleanField("Is active", default=True)

    def __str__(self):
        return self.name
