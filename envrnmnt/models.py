# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from acm.models import Institution
from prd.models import ReleasePart

WEIGHT_ARR = (
    ('Big', 'For SmartVista project - 30 Gb'),
    ('Medium', 'For SMSGate, SSO projects - 5 Gb'),
    ('Small', 'For other project - less 1 Gb'),
)


class DBInstance(models.Model):
    host = models.CharField('Host', max_length=200)
    sid = models.CharField('SID', max_length=20, blank=True, null=True, default='SV')
    port = models.IntegerField('Port', default=1521)
    login = models.CharField('DB Login', max_length=200)
    passwd = models.CharField('DB Password', max_length=200)
    sys_user = models.CharField('System Login', max_length=200, blank=True, null=True, default='system')
    sys_passwd = models.CharField('System Password', max_length=200, blank=True, null=True, default='SYSTEM1')
    weight = models.CharField('Weight', choices=WEIGHT_ARR, max_length=200, )
    content_type = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    release_part = models.ForeignKey(ReleasePart, blank=True, null=True)

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
    login = models.CharField('Login', max_length=200, default='weblogic')
    passwd = models.CharField('Password', max_length=200)
    content_type = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    release_part = models.ForeignKey(ReleasePart, blank=True, null=True)

    def __str__(self):
        return 't3://{host}:{port}'.format(host=self.host, port=self.port)

    def get_absolute_url(self):
        return reverse('webinstance-detail', kwargs={'pk': self.pk})

    def get_fields(self):
        return [(field.verbose_name, field._get_val_from_obj(self)) for field in self.__class__._meta.fields]


class STLNInstance(models.Model):
    host = models.CharField('Host', max_length=200)
    port = models.IntegerField('Port', default=22)
    user = models.CharField('User', max_length=200, default='svfe')
    passwd = models.CharField('Password', max_length=200)
    content_type = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    release_part = models.ForeignKey(ReleasePart, blank=True, null=True)

    def __str__(self):
        return '{user}@{host}'.format(host=self.host, user=self.user)

    def get_absolute_url(self):
        return reverse('stlninstance-detail', kwargs={'pk': self.pk})

    def get_fields(self):
        return [(field.verbose_name, field._get_val_from_obj(self)) for field in self.__class__._meta.fields]


class Environment(models.Model):
    name = models.CharField('Name', max_length=200, unique=True)
    is_active = models.BooleanField("Is active", default=True)
    dbinstances = GenericRelation(DBInstance)
    webinstances = GenericRelation(WEBInstance)
    stlninstances = GenericRelation(STLNInstance)
    inst = models.ForeignKey(Institution, verbose_name='Group')

    def __str__(self):
        return self.name

    def get_fields(self):
        return [(field.verbose_name, field._get_val_from_obj(self)) for field in self.__class__._meta.fields]

    def get_absolute_url(self):
        return reverse('env-detail', kwargs={'pk': self.pk})
