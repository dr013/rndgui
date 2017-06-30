# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings


class JiraFilter(models.Model):
    empl = models.ForeignKey(User)
    jira_filter = models.IntegerField(_("Jira  filter"))

    @property
    def jira_url(self):
        return '{jira}/issues/?filter={id}'.format(jira=settings.JIRA_URL, id=self.jira_filter)


class JiraReportField(models.Model):
    jira_filter = models.ForeignKey(JiraFilter)
    order = models.PositiveSmallIntegerField(_("Field order"))
    field_name = models.CharField(_("Field name"), max_length=200)
