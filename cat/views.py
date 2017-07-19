# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.urls import reverse_lazy
from django.shortcuts import HttpResponseRedirect, render
from django.views.generic import ListView, CreateView, DeleteView, DetailView, UpdateView, TemplateView
from .models import *
from .forms import ReleaseForm, RCarouselForm
from .tasks import get_stand, release_stand, up_release, down_release
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from envrnmnt.serializers import EnvironmentSerializer

# Get an instance of a logger
logger = logging.getLogger(__name__)


def reset_counter():
    """
        Method for reset used counter at rCarousel
    """
    logger.info("Reset used counter in Carousel releases")
    all_releases = ReleaseCarousel.objects.all()
    for release in all_releases:
        logger.info("Release [{r}] was reset".format(r=release))
        release.count = 0
        release.save()


def up_release_to_test(request, pk):
    data = up_release(pk=pk)
    if data:
        message = 'Release [{r}] was upped to testing!'.format(r=data)
        messages.success(request, message)
    else:
        message = 'Something went wrong!'
        messages.info(request, message)

    return HttpResponseRedirect('/test-env/rcarousel-list')


def down_release_to_test(request, pk):
    data = down_release(pk=pk)
    if data:
        message = 'Release [{r}] was downed to testing!'.format(r=data)
        messages.success(request, message)
    else:
        message = 'Something went wrong!'
        messages.info(request, message)

    return HttpResponseRedirect('/test-env/rcarousel-list')


def create_rcarousel(request):
    if request.method == "POST":
        form = RCarouselForm(data=request.POST)
        if form.is_valid():
            reset_counter()
            rcarousel = form.save(commit=False)
            rcarousel.last_used_at = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())
            rcarousel.save()
            return HttpResponseRedirect('/test-env/rcarousel-list')
    else:
        form = RCarouselForm()
    return render(request, 'cat/releasecarousel_form.html', locals())


class UpdateRCarousel(UpdateView):
    model = ReleaseCarousel
    fields = ['release', 'count', 'sort', 'is_active']
    success_message = 'Release of carousel was updated successfully.'

    def form_valid(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(UpdateRCarousel, self).form_valid(request, *args, **kwargs)


class DeleteRCarousel(DeleteView):
    model = ReleaseCarousel
    success_url = reverse_lazy('rcarousel-list')
    success_message = 'Release was deleted from carousel successfully.'
    template_name = "cat/testenvironment_confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteRCarousel, self).delete(request, *args, **kwargs)


class RCarouselDetail(DetailView):
    model = ReleaseCarousel


class RCarouselList(ListView):
    model = ReleaseCarousel


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
    fields = ['name', 'env', 'prd', 'is_active', 'expire']
    success_message = 'Test stand was updated successfully.'
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
    fields = ['name', 'env', 'prd', 'is_active', 'expire']
    success_message = 'Test stand was created successfully.'
    template_name = "cat/testenvironment_form.html"

    def form_valid(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(CreateTestEnv, self).form_valid(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CreateTestEnv, self).get_context_data(**kwargs)
        context['list_url'] = "test-env-list"
        return context


def acquire_stand(request):
    """
        Get FREE stand for testing in manual running
        :param request:
        :return:
    """
    model = TestEnvironment()
    if request.method == "POST":
        form = ReleaseForm(data=request.POST)
        if form.is_valid():
            release = Release.objects.get(pk=request.POST['release'])
            stand = get_stand(release=release.name)
            if stand:
                message = 'Stand [{st}] was acquire for testing release [{r}]'.format(st=stand, r=release.name)
                messages.success(request, message)
            else:
                message = 'No free stands!'
                messages.info(request, message)
            return HttpResponseRedirect('/test-env/test-env-list')
    else:
        form = ReleaseForm()
        return render(request, 'cat/release_form.html', locals())


def release_stand_api(request):
    """
        View method for accept request from jenkins task to release autoTest server
        :param request: GET param 'hash=' and 'force='
        :return: true or false by result of released
    """
    data = ""
    force = False
    if "hash" in request.GET and request.GET['hash']:
        hash_param = request.GET['hash']
        logger.info("Request release's stand by hash [{h}]".format(h=hash_param))
        if 'force' in request.GET:
            logger.info("At request find [force] key. Jenkins task will be aborted".format(h=hash_param))
            force = True

        if 'status' in request.GET:
            status = request.GET['status']
        else:
            status = 'completed'

        data = release_stand(hash_code=hash_param, force=force, status=status)
        if data:
            return HttpResponse(data.stand)
        else:
            return HttpResponse(data)
    else:
        logger.info("Request release's stand did't has hash parameter")
        return HttpResponse(data)


def release_stand_hash(request, hash_code):
    """
        View for release stand from UI interface
        :param request: django build-in parameter of HTTP request
        :param hash_code: stand-hash parameter
        :return: redirect to AutoTest list    """

    logger.info("Manual request release's stand by hash [{h}]".format(h=hash_code))
    data = release_stand(hash_code=hash_code, force=True, status='abort')
    if data:
        message = 'Stand [{st}] was released!'.format(st=data.stand)
        messages.success(request, message)
    else:
        message = 'Something went wrong!'
        messages.info(request, message)

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


def stand_to_json(request, stand_name):
    """
        Method for Serializing Stand object
        :param request:
        :param stand_name:
        :return:
    """
    stand = TestEnvironment.objects.get(name=stand_name)
    env = Environment.objects.get(pk=stand.pk)
    json = EnvironmentSerializer(env)
    return JsonResponse(json.data, safe=False)
