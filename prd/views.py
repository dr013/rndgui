# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required, permission_required
from .models import *
from django.shortcuts import render
from django.views.generic import ListView


@login_required
@permission_required('prd.add_build')
def create_build(request):
    if request.user.is_authenticated():
        username = request.user.username
        prd_list = Product.objects.all()

    return render(request, 'create_build.html', locals())


class ReleaseList(ListView):
    model = Release
