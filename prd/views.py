# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse_lazy
from django.forms import formset_factory
from prd.forms import ReleaseForm, BuildRevisionForm
from .models import *
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView


class ReleaseList(ListView):
    model = Release


class ProductList(ListView):
    model = Product


class BuildList(ListView):
    model = Build


@login_required
@permission_required('prd.add_build')
def create_build1(request, product=None):
    product_obj = Product.objects.get(jira=product.upper())

    if request.method == 'GET' and product:  # set product

        form = ReleaseForm(product_obj)
        phase = 2
    elif request.method == 'POST':  # create build
        form = ReleaseForm(product_obj, request.POST)
        if form.is_valid():
            release = form.cleaned_data['release']
            product_id = form.cleaned_data['product']
            build = Build.objects.get(released=False)
            release_part = ReleasePart.objects.filter(product__pk=product_id, release__isnull=True)
            init_form = [{"module": x.name} for x in release_part]
            release_part_cnt = release_part.count()
            build_revision_formset = formset_factory(BuildRevisionForm, max_num=release_part_cnt)
            formset = build_revision_formset(initial=init_form)
            phase = 3
        else:
            form = ReleaseForm(product_obj, request.POST)
            phase = 2

    else:
        phase = 1

    return render(request, 'prd/create_build.html', locals())


@login_required
@permission_required('prd.add_build')
def create_build2(request):
    build_revision_formset = formset_factory(BuildRevisionForm)
    formset = build_revision_formset(request.POST)
    if formset.is_valid():
        for rec in formset:
            print rec

    current_build = Build.objects.get(released=False)
    current_build.released = True
    current_build.date_released = datetime.datetime.now()
    current_build.save()
    next_number = str(int(current_build.name) + 1)
    new_build = Build.objects.create(released=False, name=next_number, release=current_build.release,
                                     author=request.user, is_active=True)
    new_build.save()
    return render(request, 'prd/process_create_build.html', locals())


class HotFixList(ListView):
    model = HotFix


class ProductReleaseList(ListView):
    jira_project_list()

    def get_queryset(self):
        self.product = get_object_or_404(Product, jira=self.args[0].upper())
        return Release.objects.filter(product=self.product).order_by('-date_released')


class ReleaseBuildList(ListView):
    def get_queryset(self):
        self.release = get_object_or_404(Release, pk=self.kwargs['pk'])
        return Build.objects.filter(release=self.release).order_by('-date_released')


class CreateProduct(CreateView):
    model = Product
    fields = ['title', 'desc', 'wiki_url', 'jira', 'inst', 'owner']


class UpdateProduct(UpdateView):
    model = Product
    fields = ['title', 'desc', 'wiki_url', 'jira', 'inst', 'owner']


class DeleteProduct(DeleteView):
    model = Product
    success_url = reverse_lazy('product-list')


class ProductDetail(DetailView):
    model = Product

    def get_context_data(self, **kwargs):
        context = super(ProductDetail, self).get_context_data(**kwargs)
        context['release_part'] = ReleasePart.objects.filter(product=self.object.pk, release__isnull=True)
        return context


class ReleaseDetail(DetailView):
    model = Release
