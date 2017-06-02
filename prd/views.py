# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse_lazy
from django.forms import formset_factory
from django.views.decorators.cache import never_cache

from prd.forms import ReleaseForm, BuildRevisionForm, ProductForm
from .models import *
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib import messages

# Get an instance of a logger
logger = logging.getLogger(__name__)


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
    messages.add_message(request, messages.SUCCESS, 'First build was created!')
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
    form_class = ProductForm
    success_message = "%(title)s was created successfully"


class UpdateProduct(UpdateView):
    model = Product
    form_class = ProductForm


class DeleteProduct(DeleteView):
    model = Product
    success_url = reverse_lazy('product-list')


class ProductDetail(DetailView):
    model = Product

    def get_context_data(self, **kwargs):
        context = super(ProductDetail, self).get_context_data(**kwargs)
        context['release_part'] = ReleasePart.objects.filter(product=self.object.pk, release__isnull=True)
        return context


class BuildDetail(DetailView):
    model = Build


class ReleaseDetail(DetailView):
    model = Release


class ReleasePartCreate(CreateView):
    model = ReleasePart
    fields = ['name', 'product', 'gitlab_id']
    success_message = "%(name)s was created successfully"

    def get_success_url(self, **kwargs):
        if kwargs:
            return reverse_lazy('product-detail', kwargs={'pk': self.kwargs.get('product')})
        else:
            return reverse_lazy('product-list')

    def get_initial(self):
        product = get_object_or_404(Product, pk=self.kwargs.get('product'))
        return {
            'product': product,
        }


class ReleasePartDelete(DeleteView):
    model = ReleasePart
    success_message = "Release part was deleted successfully"
    success_url = reverse_lazy('product-list')


class ReleasePartUpdate(UpdateView):
    model = ReleasePart
    success_message = "Release part %(name) was updated successfully"
    fields = ['name', 'product', 'gitlab_id']


class HotFixCreate(CreateView):
    model = HotFix
    fields = ['name', 'build', 'jira']
    success_message = "%(name)s was created successfully!"
