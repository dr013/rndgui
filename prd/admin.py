# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from prd.models import Product, Release, Build, HotFix, ReleasePart, BuildRevision
from simple_history.admin import SimpleHistoryAdmin


class BuildInline(admin.TabularInline):
    model = Build


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


admin.site.register(Product, ProductAdmin)
admin.site.register(Release, ReleaseAdmin)
admin.site.register(Build, BuildAdmin)
admin.site.register(HotFix, SimpleHistoryAdmin)
admin.site.register(ReleasePart, SimpleHistoryAdmin)
admin.site.register(BuildRevision, BuildRevisionAdmin)
