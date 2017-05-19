# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from prd.models import Product


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"name": ("title",)}


admin.site.register(Product, ProductAdmin)
