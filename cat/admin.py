# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from .models import *
# Register your models here.


class TestEnvironmentAdmin(admin.ModelAdmin):
    list_filter = ['env', ]
    list_display = ['id', 'name', 'env', 'prd', 'is_active', 'expire']


class UsageLogAdmin(admin.ModelAdmin):
    list_filter = ['stand', ]
    list_display = ['id', 'stand', 'release', 'status', 'started_at', 'task', 'hash', 'finished_at']


admin.site.register(TestEnvironment, TestEnvironmentAdmin)
admin.site.register(UsageLog, UsageLogAdmin)
