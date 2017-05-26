# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.urls import reverse
from django.contrib.auth.models import User
from django.db import models
from simple_history.models import HistoricalRecords
from acm.models import Institution
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from prd.api import GitLab


def getkey(item):
    return item[1]


def gilab_project_list():
    project_list = GitLab().project_list()
    short_list = ((x.id, x.name_with_namespace) for x in project_list)
    return sorted(short_list, key=getkey)


def gitlab_project(pid):
    obj = GitLab().project(pid)
    if obj:
        return obj
    else:
        return None


class Product(models.Model):
    title = models.CharField("Product title", max_length=200)
    desc = models.CharField("Product Description", max_length=200, null=True, blank=True)
    wiki_url = models.URLField("Wiki/Confluence URL", null=True, blank=True)
    jira = models.CharField("Jira project code", max_length=20)  # TODO add choices
    inst = models.ForeignKey(Institution, verbose_name='Group')
    owner = models.ForeignKey(User)
    is_internal = models.BooleanField("Is internal", default=False)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)
    specification_repo = models.IntegerField(_("Specifications repository"), null=True, blank=True,
                                             help_text="Gitlab repostitory ID for product specifications",
                                             choices=gilab_project_list())
    history = HistoricalRecords()

    def __str__(self):
        return "{title}: {inst}".format(title=self.title, inst=self.inst)

    def get_absolute_url(self):
        return reverse('product-detail', kwargs={'pk': self.pk})

    @property
    def name(self):
        return self.jira.lower()

    @property
    def wiki_url_link(self):
        if self.wiki_url:
            res = '<a href="{url}" targer="_blank">{url}</a>'.format(url=self.wiki_url)
        else:
            res = ''
        return res

    @property
    def jira_url_link(self):
        if self.jira:
            res = '<a href="{url}projects/{jira}" target="_blank">{jira}</a>'.format(jira=self.jira,
                                                                                     url=settings.JIRA_URL)
        else:
            res = ''
        return res


class Release(models.Model):
    name = models.CharField(_("Release number"), max_length=20)
    product = models.ForeignKey(Product)
    jira = models.CharField(_("Jira task for release"), max_length=20, blank=True, null=True)
    is_active = models.BooleanField(_("Is active"), default=True)
    released = models.BooleanField(_("Is released"), default=False)
    author = models.ForeignKey(User)
    date_released = models.DateField(_("Release date"), null=True, blank=True)
    created = models.DateField(_("Created"), auto_now_add=True)
    updated = models.DateField(_("Updated"), auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return "{rel} - {prd}".format(rel=self.name, prd=self.product)

    def get_absolute_url(self):
        return reverse('release-detail', kwargs={'pk': self.pk})

    @property
    def get_jira_url(self):
        if self.jira:
            res = '<a href="{url}/browse/{task}" target"_blank">{task}</a>' \
                .format(url=settings.JIRA_URL, task=self.jira)
        else:
            res = ''
        return res


class Build(models.Model):
    name = models.CharField("Build number", max_length=20)
    release = models.ForeignKey(Release)
    jira = models.CharField(_("Jira subtask for build"), max_length=20, null=True, blank=True)
    is_active = models.BooleanField(_("Is active"), default=True)
    released = models.BooleanField(_("Is released"), default=False)
    author = models.ForeignKey(User)
    date_released = models.DateField(_("Build date"), null=True, blank=True)
    created = models.DateField(_("Created"), auto_now_add=True)
    updated = models.DateField(_("Updated"), auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return "{prd} {rel}.{build}".format(rel=self.release.name, prd=self.release.product, build=self.name)

    def get_absolute_url(self):
        return reverse('build-detail', kwargs={'pk': self.pk})

    @property
    def full_name(self):
        return '{rel}.{bld}'.format(rel=self.release.name, bld=self.name)

    @property
    def git_name(self):
        return 'v' + self.full_name

    @property
    def get_jira_url(self):
        if self.jira:
            res = '<a href="{url}/browse/{task}" target"_blank">{task}</a>' \
                .format(url=settings.JIRA_URL, task=self.jira)
        else:
            res = ''
        return res

    def hotfix_list(self):
        """Returns the queryset of hotfix for build"""
        hotfix_list = HotFix.objects.filter(build=self.pk).order_by('-date_released')
        return hotfix_list


class HotFix(models.Model):
    name = models.CharField("HotFix number", max_length=20)
    build = models.ForeignKey(Build)
    jira = models.CharField(_("Jira task for hotfix"), max_length=20, null=True, blank=True)
    author = models.ForeignKey(User)
    date_released = models.DateField(_("HotFix date"))
    created = models.DateField(_("Created"), auto_now_add=True)
    updated = models.DateField(_("Updated"), auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return "{build}.{hotfix}".format(build=self.build, hotfix=self.name)

    def get_absolute_url(self):
        return reverse('hotfix-detail', kwargs={'pk': self.pk})

    @property
    def full_name(self):
        return '{bld}.{hf}'.format(bld=self.build.full_name, hf=self.name)

    @property
    def git_name(self):
        return 'v' + self.full_name

    @property
    def get_jira_url(self):
        if self.jira:
            res = '<a href="{url}/browse/{task}" target"_blank">{task}</a>' \
                .format(url=settings.JIRA_URL, task=self.jira)
        else:
            res = ''
        return res


class ReleasePart(models.Model):
    """ Release part  - product modules configuration"""
    name = models.CharField(_("Module name"), max_length=200)
    product = models.ForeignKey(Product)
    release = models.ForeignKey(to=Release, null=True, blank=True)
    gitlab_id = models.IntegerField(_("Gitlab project"), null=True, blank=True, choices=gilab_project_list())
    history = HistoricalRecords()

    def __str__(self):
        return '{product}::{name}'.format(product=self.product.name, name=self.name)

    @property
    def gitlab_project_url(self):
        return gitlab_project(self.gitlab_id).web_url

    @property
    def gitlab_project_name(self):
        return gitlab_project(self.gitlab_id).name_with_namespace

    @property
    def gitlab_repo_ssh(self):
        return gitlab_project(self.gitlab_id).ssh_url_to_repo

    @property
    def gitlab_repo_html(self):
        return gitlab_project(self.gitlab_id).http_url_to_repo

    @property
    def gitlab_project_desc(self):
        return gitlab_project(self.gitlab_id).description


class BuildRevision(models.Model):
    build = models.ForeignKey(Build)
    release_part = models.ForeignKey(ReleasePart)
    revision = models.CharField(_("Git revision"), max_length=40)
