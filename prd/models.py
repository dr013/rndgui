# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.urls import reverse
from django.contrib.auth.models import User
from django.db import models
from acm.models import Institution
from django.utils.translation import ugettext_lazy as _


class Product(models.Model):
    title = models.CharField("Product title", max_length=200)
    desc = models.CharField("Product Description", max_length=200, null=True, blank=True)
    wiki_url = models.URLField("Wiki/Confluence URL", null=True, blank=True)
    jira = models.CharField("Jira project code", max_length=20)  # TODO add choices
    name = models.SlugField("product_name")
    inst = models.ForeignKey(Institution)
    owner = models.ForeignKey(User)
    is_internal = models.BooleanField("Is internal", default=False)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    def __str__(self):
        return "{title}: {inst}".format(title=self.title, inst=self.inst)


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

    def __str__(self):
        return "{rel} - {prd}".format(rel=self.name, prd=self.product)

    def get_absolute_url(self):
        return reverse('release-detail', kwargs={'pk': self.pk})


class Build(models.Model):
    name = models.CharField("Build number", max_length=20)
    release = models.ForeignKey(Release)
    jira = models.CharField(_("Jira subtask for build"), max_length=20)
    is_active = models.BooleanField(_("Is active"), default=True)
    released = models.BooleanField(_("Is released"), default=False)
    author = models.ForeignKey(User)
    date_released = models.DateField(_("Build date"), null=True, blank=True)
    created = models.DateField(_("Created"), auto_now_add=True)
    updated = models.DateField(_("Updated"), auto_now=True)

    def __str__(self):
        return "{prd} {rel}.{build}".format(rel=self.release.name, prd=self.release.product, build=self.name)

    def get_absolute_url(self):
        return reverse('build-detail', kwargs={'pk': self.pk})


class HotFix(models.Model):
    name = models.CharField("HotFix number", max_length=20)
    build = models.ForeignKey(Build)
    jira = models.CharField(_("Jira task for hotfix"), max_length=20)
    author = models.ForeignKey(User)
    date_released = models.DateField(_("HotFix date"))
    created = models.DateField(_("Created"), auto_now_add=True)
    updated = models.DateField(_("Updated"), auto_now=True)

    def __str__(self):
        return "{build}.{hotfix}".format(build=self.build, hotfix=self.name)
