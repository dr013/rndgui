# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse_lazy

from .models import *
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView


# from django.views.generic.edit import CreateView


@login_required
@permission_required('prd.add_build')
def create_build(request):
    username = request.user.username
    prd_list = Product.objects.all()

    return render(request, 'create_build.html', locals())


class ReleaseList(ListView):
    model = Release


class ProductList(ListView):
    model = Product


class BuildList(ListView):
    model = Build


class HotFixList(ListView):
    model = HotFix


class ProductReleaseList(ListView):

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
