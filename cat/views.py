# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import *
from django.contrib import messages


class DBInstanceList(ListView):
    model = DBInstance


class DBInstanceDetail(DetailView):
    model = DBInstance
    template_name = "cat/instance_detail.html"

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['list_url'] = "dbinstance-list"
        return context


class CreateDBInstance(CreateView):
    model = DBInstance
    fields = ['host', 'sid', 'port', 'login', 'passwd', 'sys_user', 'sys_passwd', 'weight']
    template_name = "cat/instance_form.html"

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context['list_url'] = "dbinstance-list"
        return context


class UpdateDBInstance(UpdateView):
    model = DBInstance
    fields = ['host', 'sid', 'port', 'login', 'passwd', 'sys_user', 'sys_passwd', 'weight']
    success_message = 'DB Instance was updated successfully.'
    template_name = "cat/instance_form.html"

    def form_valid(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(UpdateDBInstance, self).form_valid(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['list_url'] = "dbinstance-list"
        return context


class DeleteDBInstance(DeleteView):
    model = DBInstance
    success_url = reverse_lazy('dbinstance-list')
    success_message = 'DB Instance was deleted successfully.'
    template_name = "cat/instance_confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteDBInstance, self).delete(request, *args, **kwargs)


class WEBInstanceList(ListView):
    model = WEBInstance


class WEBInstanceDetail(DetailView):
    model = WEBInstance
    template_name = "cat/instance_detail.html"

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['list_url'] = "webinstance-list"
        return context


class CreateWEBInstance(CreateView):
    model = WEBInstance
    fields = ['host', 'port', 'target_server', 'host_login']
    template_name = "cat/instance_form.html"

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context['list_url'] = "webinstance-list"
        return context


class UpdateWEBInstance(UpdateView):
    model = WEBInstance
    fields = ['host', 'port', 'target_server', 'host_login']
    success_message = 'WEB Instance was updated successfully.'
    template_name = "cat/instance_form.html"

    def form_valid(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(UpdateWEBInstance, self).form_valid(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['list_url'] = "webinstance-list"
        return context


class DeleteWEBInstance(DeleteView):
    model = WEBInstance
    success_url = reverse_lazy('webinstance-list')
    success_message = 'WEB Instance was deleted successfully.'
    template_name = "cat/instance_confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteWEBInstance, self).delete(request, *args, **kwargs)


class STLNInstanceList(ListView):
    model = STLNInstance


class STLNInstanceDetail(DetailView):
    model = STLNInstance
    template_name = "cat/instance_detail.html"

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['list_url'] = "stlninstance-list"
        return context


class CreateSTLNInstance(CreateView):
    model = STLNInstance
    fields = ['host', 'host_login']
    template_name = "cat/instance_form.html"

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context['list_url'] = "stlninstance-list"
        return context


class UpdateSTLNInstance(UpdateView):
    model = STLNInstance
    fields = ['host', 'host_login']
    success_message = 'Standalone Instance was updated successfully.'
    template_name = "cat/instance_form.html"

    def form_valid(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(UpdateSTLNInstance, self).form_valid(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['list_url'] = "stlninstance-list"
        return context


class DeleteSTLNInstance(DeleteView):
    model = STLNInstance
    success_url = reverse_lazy('stlninstance-list')
    success_message = 'Standalone Instance was deleted successfully.'
    template_name = "cat/instance_confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteSTLNInstance, self).delete(request, *args, **kwargs)
