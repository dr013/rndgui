# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# from django.forms import formset_factory
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core import serializers
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from prd.forms import ProductForm
from .models import *

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
    build = forms.IntegerField(widget=forms.HiddenInput())

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


@login_required
@permission_required('prd.add_build')
def create_build(request, product):
    if request.method == "GET" and 'build' in request.GET:
        build_id = request.GET['build']
        build = Build.objects.get(pk=int(build_id))
        prev_data = Build.objects.get(release=build.release, name=str(int(build.name) - 1)).date_released
        pk = build.pk
        product_obj = Product.objects.get(jira=product.upper())
        form = BuildIssueForm(product=product.upper(), initial={'build': pk})
        release_part = ReleasePart.objects.filter(product=product_obj)
        rev_list = []
        for rec in release_part:
            rev_list.append({'pk': rec.id,
                             'revision_list': GitLab().get_revision_list(project_id=rec.gitlab_id,
                                                                         ref_name=build.release.dev_branch,
                                                                         since=prev_data)})
    elif request.method == "POST":

        build = Build.objects.get(pk=request.POST['build'])
        release = build.release
        product = release.product

        release_part = ReleasePart.objects.filter(product=product)
        for rec in release_part:
            post_part = 'part_{}'.format(rec.pk)
            if post_part in request.POST:
                revision = request.POST[post_part]
                rel_part = ReleasePart.objects.get(pk=rec.pk)
                bld_revision = BuildRevision()
                bld_revision.build = build
                bld_revision.release_part = rel_part
                bld_revision.revision = revision
                bld_revision.save()
                gitlab = GitLab().create_tag(project_id=rec.gitlab_id, tag=build.git_name, ref=revision,
                                             desc=build.git_name, user=request.user)
        messages.add_message(request, messages.INFO, '1. Git tags in GitLab was created successufily.')
        build.date_released = datetime.date.today()
        build.author = request.user
        build.released = True
        build.save()
        messages.add_message(request, messages.INFO, '2.1 Jira task for issued build was closed.')
        messages.add_message(request, messages.INFO, '2.2 Jira task for new build was created.')
        # todo release_author

        build_new = Build(name=str(int(build.name) + 1), release=release)
        build_new.author = request.user

        build_new.save()
        messages.add_message(request, messages.SUCCESS, 'New buiild name: {}'.format(build_new.full_name))
        messages.add_message(request, messages.WARNING, '3. Dictionary report - task not found!')
        messages.add_message(request, messages.WARNING, '4. Specification repostiory - need permissions!')
        return HttpResponseRedirect(reverse('build-list-by-release', kwargs={'pk': release.pk}))

    return render(request, 'create_build.html', locals())


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
        context['release'] = self.release
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
    fields = ['name', 'product', 'gitlab_id']
    success_message = "%(name)s was created successfully"

    def get_success_url(self, **kwargs):
        return reverse_lazy('product-detail', kwargs={'pk': self.product.pk})

    def get_initial(self):
        self.product = get_object_or_404(Product, pk=self.kwargs.get('product'))
        return {
            'product': self.product,
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
    template_name = 'hotfix_form.html'
    fields = ['name', 'build', 'jira']
    success_message = "%(name)s was created successfully!"

    def get_initial(self):
        self.build = Build.objects.get(pk=self.kwargs.get('pk'))
        hotfix = HotFix.objects.filter(build=self.build)
        logger.debug(
            'HotFix current number for build {bld} is {cnt}'.format(bld=self.build.full_name, cnt=hotfix.count()))
        if hotfix.count() == 0:
            hotfix_num = '1'
        else:
            hotfix_num = str(int(hotfix.name) + 1)
        return {
            'build': self.build,
            'name': hotfix_num
        }

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.author = self.request.user
        obj.date_released = datetime.date.today()
        # set tag
        tag_name = '{bld}.{tag}'.format(bld=self.build.git_name, tag=obj.name)
        tag_desc = 'HotFix {name} for build {bld}'.format(bld=self.build.full_name, name=obj.name)
        release_part = ReleasePart.objects.filter(product=self.build.release.product)
        for rec in release_part:
            gitlab = GitLab().create_tag(project_id=rec.gitlab_id, tag=tag_name, ref=self.build.full_name,
                                         desc=tag_desc, user=obj.author)
            logger.debug(str(gitlab))
        return super(HotFixCreate, self).form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse_lazy('build-list-by-release', kwargs={'pk': self.build.release.pk})


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
            release_full_name = self.release_list[0].name.split(".")
            if len(release_full_name) == 1:
                release_name = str(int(release_full_name[-1]) + 1)
            else:
                release_name = '{product}.{release}'.format(product=release_full_name[0],
                                                            release=int(release_full_name[1]) + 1)

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


def rest_product(request, product):
    data = get_object_or_404(Product, jira=product.upper())

    qs_json = {"title": data.title}
    return JsonResponse(qs_json, safe=False)
