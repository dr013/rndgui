# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import *


class DBInstanceAdmin(admin.ModelAdmin):
    list_filter = ['host', ]


class WEBInstanceAdmin(admin.ModelAdmin):
    list_filter = ['host', ]


class STLNInstanceAdmin(admin.ModelAdmin):
    list_filter = ['host', ]


class DBInstanceInline(GenericTabularInline):
    model = DBInstance
    extra = 1


class WEBInstanceInline(GenericTabularInline):
    model = WEBInstance
    extra = 1


class STLNInstanceInline(GenericTabularInline):
    model = STLNInstance
    extra = 1


class InstanceAdmin(admin.ModelAdmin):
    inlines = [
        DBInstanceInline,
        WEBInstanceInline,
        STLNInstanceInline,
    ]


admin.site.register(DBInstance, DBInstanceAdmin)
admin.site.register(WEBInstance, WEBInstanceAdmin)
admin.site.register(STLNInstance, STLNInstanceAdmin)
admin.site.register(Environment, InstanceAdmin)
