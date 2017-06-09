# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.urls import reverse
from envrnmnt.models import Environment
from prd.models import Product

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
    status = models.CharField('Statuses', choices=STATUSES, max_length=200, default='free')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('test-env-detail', kwargs={'pk': self.pk})

    def get_fields(self):
        return [(field.verbose_name, field._get_val_from_obj(self)) for field in self.__class__._meta.fields]
