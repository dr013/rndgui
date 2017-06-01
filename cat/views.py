# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import *
from django.contrib import messages
# Create your views here.


class InstanceList(ListView):
    model = DBInstance


class InstanceDetail(DetailView):
    model = DBInstance


class CreateInstance(CreateView):
    model = DBInstance
    fields = ['host', 'sid', 'port', 'login', 'passwd', 'sys_user', 'sys_passwd', 'weight']


class UpdateInstance(UpdateView):
    model = DBInstance
    fields = ['host', 'sid', 'port', 'login', 'passwd', 'sys_user', 'sys_passwd', 'weight']
    success_message = 'Instance was updated successfully.'

    def form_valid(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(UpdateInstance, self).form_valid(request, *args, **kwargs)


class DeleteInstance(DeleteView):
    model = DBInstance
    success_url = reverse_lazy('instance-list')
    success_message = 'Instance was deleted successfully.'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteInstance, self).delete(request, *args, **kwargs)
