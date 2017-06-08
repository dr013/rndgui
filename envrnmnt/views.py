# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.contenttypes.forms import generic_inlineformset_factory
from .models import *
from .forms import EnvForm
from django.shortcuts import render, HttpResponseRedirect, get_object_or_404
from django.contrib import messages


class EnvLint(ListView):
    model = Environment
    context_object_name = 'envs'

    def get_queryset(self):
        return Environment.objects.all()


class EnvDetail(DetailView):
    model = Environment
    context_object_name = 'env'

    def get_queryset(self):
        return Environment.objects.all()


class DeleteEnv(DeleteView):
    model = Environment
    success_url = reverse_lazy('env-list')
    success_message = 'Environment was deleted successfully.'
    template_name = "envrnmnt/instance_confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteEnv, self).delete(request, *args, **kwargs)


def CreateEnv(request):
    DBInstanceFormSet = generic_inlineformset_factory(DBInstance, extra=1, can_delete=True)
    WEBInstanceFormSet = generic_inlineformset_factory(WEBInstance, extra=1, can_delete=True)
    STLNInstanceFormSet = generic_inlineformset_factory(STLNInstance, extra=1, can_delete=True)

    if request.method == "POST":
        form = EnvForm(data=request.POST)
        if form.is_valid():
            c_env = form.save()
            formsetdb = DBInstanceFormSet(data=request.POST, instance=c_env)
            formsetweb = WEBInstanceFormSet(data=request.POST, instance=c_env)
            formsetstln = STLNInstanceFormSet(data=request.POST, instance=c_env)
            if formsetdb.is_valid() and formsetweb.is_valid() and formsetstln.is_valid():
                formsetdb.save()
                formsetweb.save()
                formsetstln.save()

                return HttpResponseRedirect('/instance/env-list')
    else:
        form = EnvForm()
        formsetdb = DBInstanceFormSet()
        formsetweb = WEBInstanceFormSet()
        formsetstln = STLNInstanceFormSet()
    return render(request, 'envrnmnt/environment_form.html', locals())


def UpdateEnv(request, pk):
    env = get_object_or_404(Environment, id=pk)
    DBInstanceFormSet = generic_inlineformset_factory(DBInstance, extra=0, can_delete=True)
    WEBInstanceFormSet = generic_inlineformset_factory(WEBInstance, extra=0, can_delete=True)
    STLNInstanceFormSet = generic_inlineformset_factory(STLNInstance, extra=0, can_delete=True)

    if request.method == "POST":
        form = EnvForm(data=request.POST, instance=env)
        formsetdb = DBInstanceFormSet(data=request.POST, instance=env)
        formsetweb = WEBInstanceFormSet(data=request.POST, instance=env)
        formsetstln = STLNInstanceFormSet(data=request.POST, instance=env)
        if form.is_valid():
            if formsetdb.is_valid() and formsetweb.is_valid() and formsetstln.is_valid():
                formsetdb.save()
                formsetweb.save()
                formsetstln.save()
                form.save()
                return HttpResponseRedirect('/instance/env-list')
    else:
        form = EnvForm(instance=env)
        formsetdb = DBInstanceFormSet(instance=env)
        formsetweb = WEBInstanceFormSet(instance=env)
        formsetstln = STLNInstanceFormSet(instance=env)
    return render(request, 'envrnmnt/environment_edit_form.html', locals())


class DBInstanceList(ListView):
    model = DBInstance


class DBInstanceDetail(DetailView):
    model = DBInstance
    template_name = "envrnmnt/instance_detail.html"

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['list_url'] = "dbinstance-list"
        return context


class CreateDBInstance(CreateView):
    model = DBInstance
    fields = ['host', 'sid', 'port', 'login', 'passwd', 'sys_user', 'sys_passwd', 'weight']
    template_name = "envrnmnt/instance_form.html"

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context['list_url'] = "dbinstance-list"
        return context


class UpdateDBInstance(UpdateView):
    model = DBInstance
    fields = ['host', 'sid', 'port', 'login', 'passwd', 'sys_user', 'sys_passwd', 'weight']
    success_message = 'DB Instance was updated successfully.'
    template_name = "envrnmnt/instance_form.html"

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
    template_name = "envrnmnt/instance_confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteDBInstance, self).delete(request, *args, **kwargs)


class WEBInstanceList(ListView):
    model = WEBInstance


class WEBInstanceDetail(DetailView):
    model = WEBInstance
    template_name = "envrnmnt/instance_detail.html"

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['list_url'] = "webinstance-list"
        return context


class CreateWEBInstance(CreateView):
    model = WEBInstance
    fields = ['host', 'port', 'target_server', 'login', 'passwd']
    template_name = "envrnmnt/instance_form.html"

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context['list_url'] = "webinstance-list"
        return context


class UpdateWEBInstance(UpdateView):
    model = WEBInstance
    fields = ['host', 'port', 'target_server', 'login', 'passwd']
    success_message = 'WEB Instance was updated successfully.'
    template_name = "envrnmnt/instance_form.html"

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
    template_name = "envrnmnt/instance_confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteWEBInstance, self).delete(request, *args, **kwargs)


class STLNInstanceList(ListView):
    model = STLNInstance


class STLNInstanceDetail(DetailView):
    model = STLNInstance
    template_name = "envrnmnt/instance_detail.html"

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['list_url'] = "stlninstance-list"
        return context


class CreateSTLNInstance(CreateView):
    model = STLNInstance
    fields = ['host', 'port', 'user', 'passwd']
    template_name = "envrnmnt/instance_form.html"

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context['list_url'] = "stlninstance-list"
        return context


class UpdateSTLNInstance(UpdateView):
    model = STLNInstance
    fields = ['host', 'port', 'user', 'passwd']
    success_message = 'Standalone Instance was updated successfully.'
    template_name = "envrnmnt/instance_form.html"

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
    template_name = "envrnmnt/instance_confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteSTLNInstance, self).delete(request, *args, **kwargs)
