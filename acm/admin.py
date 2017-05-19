# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from acm.models import Institution, Membership
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group
from .models import Role


class InstitutionAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug_name": ("inst_name",)}


class MembershipAdmin(admin.ModelAdmin):
    pass

admin.site.register(Institution, InstitutionAdmin)
admin.site.register(Membership, MembershipAdmin)
admin.site.unregister(Group)
admin.site.register(Role, GroupAdmin)
