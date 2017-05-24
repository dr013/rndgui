# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required, permission_required
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
        self.product = get_object_or_404(Product, name=self.args[0])
        return Release.objects.filter(product=self.product).order_by('-date_released')


class ReleaseBuildList(ListView):

    def get_queryset(self):
        self.release = get_object_or_404(Release, pk=self.kwargs['pk'])
        return Build.objects.filter(release=self.release).order_by('-date_released')


class CreateProduct(CreateView):
    model = Product
    fields = ['title', 'desc', 'name', 'wiki_url', 'jira', 'inst', 'owner']
    # title = models.CharField("Product title", max_length=200)
    # desc = models.CharField("Product Description", max_length=200, null=True, blank=True)
    # desc = models.CharField("Product Description", max_length=200, null=True, blank=True)
    # wiki_url = models.URLField("Wiki/Confluence URL", null=True, blank=True)
    # jira = models.CharField("Jira project code", max_length=20)  # TODO add choices
    # name = models.SlugField("product_name")
    # inst = models.ForeignKey(Institution)


class ProductDetail(DetailView):
    model = Product
