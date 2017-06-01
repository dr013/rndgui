# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import *
from django.contrib import messages
# Create your views here.


class DBInstanceList(ListView):
    model = DBInstance


class DBInstanceDetail(DetailView):
    model = DBInstance


class CreateDBInstance(CreateView):
    model = DBInstance
    fields = ['host', 'sid', 'port', 'login', 'passwd', 'sys_user', 'sys_passwd', 'weight']
    template_name = "cat/instance_form.html"


class UpdateDBInstance(UpdateView):
    model = DBInstance
    fields = ['host', 'sid', 'port', 'login', 'passwd', 'sys_user', 'sys_passwd', 'weight']
    success_message = 'DB Instance was updated successfully.'

    def form_valid(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(UpdateDBInstance, self).form_valid(request, *args, **kwargs)


class DeleteDBInstance(DeleteView):
    model = DBInstance
    success_url = reverse_lazy('instance-list')
    success_message = 'DB Instance was deleted successfully.'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteDBInstance, self).delete(request, *args, **kwargs)


class WEBInstanceList(ListView):
    model = WEBInstance


class WEBInstanceDetail(DetailView):
    model = WEBInstance


class CreateWEBInstance(CreateView):
    model = WEBInstance
    fields = ['host', 'port', 'target_server', 'host_login']
    template_name = "cat/instance_form.html"


class UpdateWEBInstance(UpdateView):
    model = WEBInstance
    fields = ['host', 'port', 'target_server', 'host_login']
    success_message = 'WEB Instance was updated successfully.'

    def form_valid(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(UpdateWEBInstance, self).form_valid(request, *args, **kwargs)


class DeleteWEBInstance(DeleteView):
    model = WEBInstance
    success_url = reverse_lazy('instance-list')
    success_message = 'WEB Instance was deleted successfully.'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteWEBInstance, self).delete(request, *args, **kwargs)


class STLNInstanceList(ListView):
    model = STLNInstance


class STLNInstanceDetail(DetailView):
    model = STLNInstance


class CreateSTLNInstance(CreateView):
    model = STLNInstance
    fields = ['host', 'host_login']
    template_name = "cat/instance_form.html"


class UpdateSTLNInstance(UpdateView):
    model = STLNInstance
    fields = ['host', 'host_login']
    success_message = 'Standalone Instance was updated successfully.'

    def form_valid(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(UpdateSTLNInstance, self).form_valid(request, *args, **kwargs)


class DeleteSTLNInstance(DeleteView):
    model = STLNInstance
    success_url = reverse_lazy('instance-list')
    success_message = 'Standalone Instance was deleted successfully.'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteSTLNInstance, self).delete(request, *args, **kwargs)