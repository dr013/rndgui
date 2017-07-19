# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import *


class JiraFilterAdmin(admin.ModelAdmin):
    pass


class JiraReportFieldAdmin(admin.ModelAdmin):
    pass


# Register your models here.
admin.site.register(JiraFilter, JiraFilterAdmin)
admin.site.register(JiraReportField, JiraReportFieldAdmin)
