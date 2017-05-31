# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import *

# Create your views here.


class InstanceList(ListView):
    model = DBInstance


class InstanceDetail(DetailView):
    model = DBInstance


class CreateInstance(CreateView):
    model = DBInstance
    fields = ['host', 'sid', 'port', 'login', 'passwd', 'dbname', 'sys_user', 'sys_passwd', 'weight']


class UpdateInstance(UpdateView):
    model = DBInstance
    fields = ['host', 'sid', 'port', 'login', 'passwd', 'dbname', 'sys_user', 'sys_passwd', 'weight']


class DeleteInstance(DeleteView):
    model = DBInstance
