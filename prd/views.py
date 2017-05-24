# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required, permission_required
from .models import *
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView


@login_required
@permission_required('prd.add_build')
def create_build(request):
    username = request.user.username
    prd_list = Product.objects.all()

    return render(request, 'create_build.html', locals())


class ReleaseList(ListView):
    model = Release


class ProductList(ListView):
    model = Product


class BuildList(ListView):
    model = Build


class HotFixList(ListView):
    model = HotFix


class ReleaseBuildList(ListView):

    def get_queryset(self):
        self.release = get_object_or_404(Release, name=self.args[0])
        return Build.objects.filter(release=self.release)

