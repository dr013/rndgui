# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import DBInstance
# Register your models here.


class DBInstanceAdmin(SimpleHistoryAdmin):
    pass


admin.site.register(DBInstance, DBInstanceAdmin)
