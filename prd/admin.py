# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from prd.models import Product, Release, Build, HotFix


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"name": ("jira",)}


class ReleaseAdmin(admin.ModelAdmin):
    pass


class BuildAdmin(admin.ModelAdmin):
    pass


class HotFixAdmin(admin.ModelAdmin):
    pass


admin.site.register(Product, ProductAdmin)
admin.site.register(Release, ReleaseAdmin)
admin.site.register(Build, BuildAdmin)
admin.site.register(HotFix, HotFixAdmin)
