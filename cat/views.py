# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.urls import reverse_lazy
from django.shortcuts import HttpResponseRedirect, get_object_or_404
from django.views.generic import ListView, CreateView, DeleteView, DetailView, UpdateView, TemplateView
from .models import *
from django.contrib import messages
from django.http import JsonResponse

# Get an instance of a logger
logger = logging.getLogger(__name__)


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


def acquire_stand(request):
    model = TestEnvironment()
    #   TODO get Release by 'stand.product'
    release = Release.objects.get(pk=1)
    model.acquire(user=request.user, release=release)
    #   TODO add 'human'-response
    return HttpResponseRedirect('/test-env/test-env-list')


def release_stand(request):
    """
        View method for accept request from jenkins task to release autoTest server
        :param request: GET param 'hash=' and 'force='
        :return: true or false by result of released
    """
    model = TestEnvironment()
    data = False
    force = False
    if "hash" in request.GET:
        hash_param = request.GET['hash']
        logger.info("Request release's stand by hash [h]".format(h=hash_param))
        if 'force' in request.GET:
            logger.info("At request find [force] key. Jenkins task will be aborted".format(h=hash_param))
            force = True
        data = model.release(hash=hash_param, force=force)
    return JsonResponse(data, safe=False)


def release_stand_hash(request, hash):
    """
        View for release stand from UI interface
        :param request: django build-in parameter of HTTP request
        :param hash: stand-hash parameter
        :return: redirect to AutoTest list
    """
    model = TestEnvironment()
    logger.info("Manual request release's stand by hash [{h}]".format(h=hash))
    data = model.release(hash=hash, force=True)
    if data:
        message = 'Stand [{st}] was released!'.format(st=data)
        messages.success(request, message)
    else:
        message = 'Something went wrong!'
        messages.error(request, message)

    return HttpResponseRedirect('/test-env/test-env-list')


class UsageLogByStand(TemplateView):
    model = UsageLog
    template_name = 'cat/usagelog_list.html'

    def get_context_data(self, **kwargs):
        context = super(UsageLogByStand, self).get_context_data(**kwargs)
        usage_log = UsageLog.objects.filter(stand__name=kwargs['stand_name']).order_by('-started_at')
        context['usage_log'] = usage_log
        context['stand_name'] = kwargs['stand_name']
        return context
