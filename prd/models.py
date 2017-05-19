# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from acm.models import Institution


class Product(models.Model):
    name = models.SlugField("product_name")
    title = models.CharField("Product title", max_length=200)
    desc = models.CharField("Product Description", max_length=200, null=True, blank=True)
    wiki_url = models.URLField("Wiki/Confluence URL")
    jira = models.CharField("Jira project code", max_length=20) # TODO add choices
    inst = models.ForeignKey(Institution)
    owner = models.ForeignKey(User)
    is_internal = models.BooleanField("Is internal", default=False)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    def __str__(self):
        return "{title}: {inst}".format(title=self.title, inst=self.inst)
