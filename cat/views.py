# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.urls import reverse_lazy
from django.shortcuts import HttpResponseRedirect
from django.views.generic import ListView, CreateView, DeleteView, DetailView, UpdateView
from .models import *
from django.contrib import messages
# Create your views here.


class TestEnvList(ListView):
    model = TestEnvironment
    context_object_name = 'tenv'


class DeleteTestEnv(DeleteView):
    model = TestEnvironment
    success_url = reverse_lazy('test-env-list')
    success_message = 'Environment was deleted successfully.'
    template_name = "cat/testenvironment_confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteTestEnv, self).delete(request, *args, **kwargs)


class TestEnvDetail(DetailView):
    model = TestEnvironment
    template_name = "cat/testenvironment_detail.html"

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['list_url'] = "test-env-list"
        return context


class UpdateTestEnv(UpdateView):
    model = TestEnvironment
    fields = ['name', 'env', 'prd', 'expire']
    success_message = 'Test env was updated successfully.'
    template_name = "cat/testenvironment_form.html"

    def form_valid(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(UpdateTestEnv, self).form_valid(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UpdateTestEnv, self).get_context_data(**kwargs)
        context['list_url'] = "test-env-list"
        return context


class CreateTestEnv(CreateView):
    model = TestEnvironment
    fields = ['name', 'env', 'prd', 'expire']
    success_message = 'Test env was created successfully.'
    template_name = "cat/testenvironment_form.html"

    def form_valid(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(CreateTestEnv, self).form_valid(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CreateTestEnv, self).get_context_data(**kwargs)
        context['list_url'] = "test-env-list"
        return context


def acquire_env(request):
    model = TestEnvironment()
    #   TODO get Release by 'stand.product'
    release = Release.objects.get(pk=1)
    model.acquire(user=request.user, release=release)
    #   TODO add 'human'-response
    return HttpResponseRedirect('/test-env/test-env-list')
