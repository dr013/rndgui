# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import *


# Register your models here.


class DBInstanceAdmin(SimpleHistoryAdmin):
    list_filter = ['host', ]


class WEBInstanceAdmin(SimpleHistoryAdmin):
    list_filter = ['host', ]


class STLNInstanceAdmin(SimpleHistoryAdmin):
    list_filter = ['host', ]


class InstanceAdmin(SimpleHistoryAdmin):
    list_filter = ['name', ]


admin.site.register(DBInstance, DBInstanceAdmin)
admin.site.register(WEBInstance, WEBInstanceAdmin)
admin.site.register(STLNInstance, STLNInstanceAdmin)
admin.site.register(Instance, InstanceAdmin)
