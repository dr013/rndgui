# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User, Group
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Institution(models.Model):
    inst_name = models.CharField(_("Group name"), max_length=200)
    slug_name = models.SlugField()
    user = models.ManyToManyField(User, through=_('Membership'))

    def __str__(self):  # __unicode__ on Python 2
        return self.inst_name

    class Meta:
        verbose_name = _('Group')
        verbose_name_plural = _('Groups')


class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Institution, on_delete=models.CASCADE)
    date_joined = models.DateField(auto_now_add=True)
    is_head = models.BooleanField(default=False)

    def __str__(self):  # __unicode__ on Python 2
        return '{user}::{group}'.format(user=self.user.username, group=self.group)


class Role(Group):
    class Meta:
        proxy = True
        app_label = 'auth'
        verbose_name = _('Role')
