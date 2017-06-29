# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import JiraFilter
from prd.api import JiraProject

logger = logging.getLogger(__name__)


class JiraFilterList(ListView):
    model = JiraFilter
    template_name = 'jirafilter_list.html'

    def get_queryset(self):
        self.user = self.request.user
        return JiraFilter.objects.filter(empl=self.user)

    def get_context_data(self, **kwargs):
        context = super(JiraFilterList, self).get_context_data(**kwargs)
        context['jira_list'] = JiraProject(user=self.request.user.username,
                                           password=self.request.session["secret"]).get_favorive_filter()

        return context


class JiraFilterDetail(DetailView):
    model = JiraFilter


class JiraFilterAdd(CreateView):
    model = JiraFilter
    fields = ['empl', 'jira_filter']
    template_name = 'jirafilter_form.html'


class JiraFilterModify(UpdateView):
    model = JiraFilter


class JiraFilterDelete(DeleteView):
    model = JiraFilter
