# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from envrnmnt.models import Environment

# Create your models here.


class TestEnvironment(models.Model):
    env = models.ForeignKey(Environment, verbose_name='Environment')

