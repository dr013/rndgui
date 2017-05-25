# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from prd.models import Product, Release, Build, HotFix, ReleasePart
from simple_history.admin import SimpleHistoryAdmin


class ProductAdmin(admin.ModelAdmin):
    list_filter = ('inst',)


class ReleaseAdmin(SimpleHistoryAdmin):
    list_filter = ('product',)


class BuildAdmin(admin.ModelAdmin):
    list_filter = ('release__product',)


class HotFixAdmin(admin.ModelAdmin):
    pass


class ReleasePartAdmin(admin.ModelAdmin):
    pass

admin.site.register(Product, ProductAdmin)
admin.site.register(Release, ReleaseAdmin)
admin.site.register(Build, BuildAdmin)
admin.site.register(HotFix, SimpleHistoryAdmin)
admin.site.register(ReleasePart, ReleasePartAdmin)
