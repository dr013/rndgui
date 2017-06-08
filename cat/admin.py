# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from simple_history.admin import SimpleHistoryAdmin
from django.contrib import admin
from .models import *
# Register your models here.


class TestEnvironmentAdmin(SimpleHistoryAdmin):
    list_filter = ['env', ]


admin.site.register(TestEnvironment, TestEnvironmentAdmin)
