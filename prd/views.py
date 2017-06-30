# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# from django.forms import formset_factory
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from prd.forms import ProductForm
from .models import *

# Get an instance of a logger
logger = logging.getLogger(__name__)


class ReleaseList(ListView):
    model = Release


class ProductList(ListView):
    model = Product


class BuildList(ListView):
    model = Build


CHOICE = (
    ('-1', '1.1.1'),
)


def jira_add_comment(jira_task, comment):
    jira = JiraProject()
    jira.add_comment(jira_task, comment)


class BuildIssueForm(forms.Form):
    release = forms.ChoiceField(choices=CHOICE, disabled=True)
    build = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, product, *args, **kwargs):
        super(BuildIssueForm, self).__init__(*args, **kwargs)
        self.fields['release'] = forms.ChoiceField(
            choices=[(o.id, str(o)) for o in Release.objects.filter(product__jira=product)], disabled=True
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
        form = BuildIssueForm(product=product.upper(), initial={'build': pk, 'release': build.release.pk})
        release_part = ReleasePart.objects.filter(product=product_obj)
        rev_list = []
        for rec in release_part:
            revision_list = GitLab().get_revision_list(project_id=rec.gitlab_id,
                                                       ref_name=build.release.dev_branch,
                                                       since=prev_data)
            rev_list.append({'pk': rec.id,
                             'revision_list': revision_list,
                             'count': len(revision_list)})
    elif request.method == "POST":
        res = True
        build = Build.objects.get(pk=request.POST['build'])
        release = build.release
        product = release.product

        release_part = ReleasePart.objects.filter(product=product)
        for rec in release_part:
            post_part = 'part_{}'.format(rec.pk)
            if post_part in request.POST:
                revision = request.POST[post_part]
                rel_part = ReleasePart.objects.get(pk=rec.pk)
                revision = GitLab().create_tag(project_id=rec.gitlab_id, tag=build.git_name, ref=revision,
                                               desc=build.git_name, user=request.user, ref_type='revision')
                if revision:
                    bld_revision = BuildRevision()
                    bld_revision.build = build
                    bld_revision.release_part = rel_part
                    bld_revision.revision = revision
                    bld_revision.save()
                    result = 'Tag {tag} was successful created for module {module}'.format(tag=build.full_name,
                                                                                           module=rec.name)
                    messages.add_message(request, messages.SUCCESS, result)
                else:
                    res = False
                    result = "Tag {tag} wasn't created for module {module}.".format(tag=build.full_name,
                                                                                    module=rec.name)
                    messages.add_message(request, messages.ERROR, result)

        if res:
            messages.add_message(request, messages.INFO, '1. Git tags in GitLab was created successufily.')
            build.date_released = datetime.datetime.today()
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
        hotfix = HotFix.objects.filter(build=self.build).order_by('-date_released')
        logger.debug(
            'HotFix current number for build {bld} is {cnt}'.format(bld=self.build.full_name, cnt=hotfix.count()))
        if hotfix.count() == 0:
            hotfix_num = '1'
        else:
            hotfix_num = str(int(hotfix[0].name) + 1)
        return {
            'build': self.build,
            'name': hotfix_num
        }

    def get_context_data(self, **kwargs):
        context = super(HotFixCreate, self).get_context_data(**kwargs)
        context['build'] = self.build
        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.author = self.request.user
        obj.date_released = datetime.date.today()
        obj.save()
        # set tag
        tag_name = '{bld}.{tag}'.format(bld=self.build.git_name, tag=obj.name)
        tag_desc = 'HotFix {name} for build {bld}'.format(bld=self.build.full_name, name=obj.name)
        release_part = ReleasePart.objects.filter(product=self.build.release.product)
        comment = ""
        for rec in release_part:
            revision = GitLab().create_tag(project_id=rec.gitlab_id, tag=tag_name, ref=self.build.full_name,
                                           desc=tag_desc,
                                           user=obj.author.username, ref_type='branch')
            if revision:
                hotfix_rev = HotFixRevision(hotfix=obj, release_part=rec, revision=revision)
                hotfix_rev.save()
                gl_project = GitLab().get_project(pid=rec.gitlab_id)
                comment += "Hotfix {hf} was released - {gitlab}/tags/{hf}\n".format(hf=tag_name,
                                                                                    gitlab=gl_project.web_url)
        if obj.jira:
            jira_add_comment(obj.jira, comment)
        messages.add_message(self.request, messages.SUCCESS, 'New HotFix {} was issued!'.format(tag_name))
        return super(HotFixCreate, self).form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse_lazy('build-list-by-release', kwargs={'pk': self.build.release.pk})


class ReleaseCreate(CreateView):
    model = Release
    template_name = 'release_form.html'
    fields = ['name', 'product', ]

    def get_initial(self):
        self.product = get_object_or_404(Product, jira=self.kwargs.get('product').upper())
        self.release_list = Release.objects.all().filter(product=self.product).order_by('-created')
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
        messages.add_message(self.request, messages.SUCCESS, 'New release {} was created!'.format(form.instance.name))
        return super(ReleaseCreate, self).form_valid(form)


def rest_product(request, product):
    data = get_object_or_404(Product, jira=product.upper())

    qs_json = {"title": data.title, 'jira': data.jira, 'owner': data.owner.username, 'desc': data.desc}

    return JsonResponse(qs_json)


@login_required
def release_issue(request, pk):
    release = Release.objects.get(pk=pk)
    release_part = ReleasePart.objects.filter(product=release.product)
    logger.info("Start issue release {}".format(release.name))
    if 'future' in release.dev_branch:
        new_dev_branch = '{}-develop'.format(release.name)
        new_master_branch = '{}-master'.format(release.name)
        rls_arr = release.name.split('.')
        if len(rls_arr)==2:
            next_release = '{v}.{r}'.format(v=rls_arr[0], r=str(int(rls_arr)+1))
        elif len(rls_arr) ==1:
            next_release = str(int(rls_arr)+1)
        else:
            next_release = '1'

        # create new branches
        for part in release_part:
            gl = GitLab().get_gl()
            gl.project_branches.create({'branch_name': new_dev_branch,
                                        'ref': 'future'},
                                       project_id=part.gitlab_id)

            gl.project_branches.create({'branch_name': new_master_branch,
                                        'ref': 'future'},
                                       project_id=part.gitlab_id)

            data = {
                'branch_name': 'future',
                'commit_message': '{} - bump release file.'.format(release.jira),
                'actions': [
                    {
                        'action': 'modify',
                        'file_path': 'RELEASE',
                        'content': next_release
                    }
                ]
            }

            commit = gl.project_commits.create(data, project_id=part.gitlab_id)
            logger.info(str(commit))
            logger.info("Bump release for {}".format(next_release))
        release.released = True
        release.date_released = datetime.datetime.today()
        release.save()
        messages.add_message(request, messages.SUCCESS, 'Release {} was issued!'.format(release.name))

    return HttpResponseRedirect(reverse('release-list-by-product', args=(release.product.name)))
