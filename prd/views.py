# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy
from django.forms import formset_factory
from django import forms

from prd.forms import ReleaseForm, ProductForm
from .models import *
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib import messages

# Get an instance of a logger
logger = logging.getLogger("prd")


class ReleaseList(ListView):
    model = Release


class ProductList(ListView):
    model = Product


class BuildList(ListView):
    model = Build


CHOICE = (
    ('-1', '2.14.1'),
)


class BuildIssueForm(forms.Form):
    release = forms.ChoiceField(choices=CHOICE)
    build = forms.ChoiceField(choices=CHOICE, widget=forms.Select())

    def __init__(self, product, *args, **kwargs):
        super(BuildIssueForm, self).__init__(*args, **kwargs)
        self.fields['release'] = forms.ChoiceField(
            choices=[(o.id, str(o)) for o in Release.objects.filter(product__jira=product)]
        )


class BuildRevisionForm(forms.ModelForm):
    class Meta:
        model = BuildRevision
        fields = ['release_part', 'revision']


def feeds_build(request, release_id):
    from django.core import serializers
    json_build = serializers.serialize("json", Build.objects.filter(release__pk=release_id))
    return HttpResponse(json_build, mimetype="application/javascript")


def create_build(request, product):
    product_obj = Product.objects.get(jira=product.upper())
    form1 = BuildIssueForm(product=product.upper())
    num_of_form = ReleasePart.objects.filter(product__jira=product.upper()).count()
    revision_form_set = formset_factory(BuildRevisionForm, extra=num_of_form)

    if request.method == "POST":
        form = BuildIssueForm(request.POST, request.FILES)
        rev_formset = revision_form_set(request.POST, request.FILES, prefix='rev')
        if rev_formset.is_valid() and form.is_valid():
            form.save()
            rev_formset.save()
            # Do something. Should generally end with a redirect. For example:
            return HttpResponseRedirect('start')
    else:
        form = form1
        rev_formset = revision_form_set()
    return render(request, 'create_build.html', {'formset': rev_formset, 'form': form, 'product_obj': product_obj})


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

    return render(request, 'create_build.html', locals())


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

    def get_context_data(self, **kwargs):
        context = super(ProductReleaseList, self).get_context_data(**kwargs)
        context['product'] = self.product
        return context


class ReleaseBuildList(ListView):
    def get_queryset(self):
        self.release = get_object_or_404(Release, pk=self.kwargs['pk'])
        return Build.objects.filter(release=self.release).order_by('-date_released')

    def get_context_data(self, **kwargs):
        context = super(ReleaseBuildList, self).get_context_data(**kwargs)
        context['product'] = self.release.product
        return context


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
    fields = ['name', 'product', 'gitlab_id', 'work_branch']
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
    fields = ['name', 'product', 'gitlab_id', 'work_branch']


class HotFixCreate(CreateView):
    model = HotFix
    fields = ['name', 'build', 'jira']
    success_message = "%(name)s was created successfully!"


class ReleaseCreate(CreateView):
    model = Release
    template_name = 'release_form.html'
    fields = ['name', 'product', ]

    def get_initial(self):
        self.product = get_object_or_404(Product, jira=self.kwargs.get('product').upper())
        self.release_list = Release.objects.all().filter(product=self.product).order_by('-name')
        if self.release_list.count() == 0:
            release_name = '1.0'
        else:
            release_full_name = self.release_list[0]['name'].split(".")
            if len(release_full_name) == 1:
                release_name = int(release_full_name + 1)
            else:
                release_name = '{product}.{release}'.format(product=release_full_name[0],
                                                            release=int(release_full_name) + 1)

        return {
            'product': self.product,
            'name': release_name,
        }

    def get_success_url(self):
        return reverse('build-list-by-release', args=(self.object.id,))

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ReleaseCreate, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['product'] = self.product
        return context

    def form_valid(self, form):
        user = self.request.user
        form.instance.author = user
        return super(ReleaseCreate, self).form_valid(form)
