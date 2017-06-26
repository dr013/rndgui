# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from prd.models import Product, Release, Build, HotFix, ReleasePart, BuildRevision, HotFixRevision
from simple_history.admin import SimpleHistoryAdmin


class BuildInline(admin.TabularInline):
    model = Build


class BuildRevisionInline(admin.TabularInline):
    model = BuildRevision


class ProductAdmin(SimpleHistoryAdmin):
    list_filter = ('inst',)


class ReleaseAdmin(SimpleHistoryAdmin):
    list_filter = ('product',)
    list_display = ['name', 'product', 'jira', 'is_active', 'author', 'date_released']
    inlines = [
        BuildInline,
    ]


class BuildAdmin(SimpleHistoryAdmin):
    list_filter = ('release__product', 'release')


class BuildRevisionAdmin(SimpleHistoryAdmin):
    list_filter = ('build__release__product',)
    inlines = [
        BuildRevisionInline,
    ]


class HotFixRevisionInline(admin.TabularInline):
    model = HotFixRevision


class HotFixAdmin(SimpleHistoryAdmin):
    list_display = ['full_name', 'build', 'jira', 'author', 'date_released']
    inlines = [
        HotFixRevisionInline
    ]


admin.site.register(Product, ProductAdmin)
admin.site.register(Release, ReleaseAdmin)
admin.site.register(Build, BuildAdmin)
admin.site.register(HotFix, HotFixAdmin)
admin.site.register(ReleasePart, SimpleHistoryAdmin)
admin.site.register(BuildRevision, BuildRevisionAdmin)
