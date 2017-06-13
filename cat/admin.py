# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from .models import *
# Register your models here.


class TestEnvironmentAdmin(admin.ModelAdmin):
    list_filter = ['env', ]


class UsageLogAdmin(admin.ModelAdmin):
    list_filter = ['stand', ]


admin.site.register(TestEnvironment, TestEnvironmentAdmin)
admin.site.register(UsageLog, UsageLogAdmin)
