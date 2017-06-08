# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import ListView
from .models import *
# Create your views here.


class TestEnvList(ListView):
    model = TestEnvironment

    def get_queryset(self):
        return TestEnvironment.objects.all()
