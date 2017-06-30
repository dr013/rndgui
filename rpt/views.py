# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from .models import JiraFilter
from prd.api import JiraProject
from django import forms
from django.contrib.auth.decorators import login_required
from rpt.api import excel_by_filter

logger = logging.getLogger(__name__)

INTERVAL_CHOICE = [
    ('0', 'Every work day'),
    ('1', 'On Monday'),
    ('2', 'On Friday'),
]


class JiraFilterForm(forms.Form):
    jira_filter = forms.ChoiceField(choices=[], label='Jira filter')
    interval = forms.ChoiceField(choices=INTERVAL_CHOICE, label='Send interval')


@login_required
def create_filter(request):

    if request.method == "GET":
        form = JiraFilterForm()
        jira_list = JiraProject(user=request.user.username, password=request.session["secret"]).get_favorive_filter()
        jira_choice = [('-1', '---------')]
        jira_used_list = JiraFilter.objects.filter(empl=request.user).values_list('jira_filter')
        jira_choice.extend([(x.id, x.name) for x in jira_list if x.id not in jira_used_list])
        form.fields['jira_filter'].choices = jira_choice
    elif request.method == "POST":
        jf = JiraFilter(empl=request.user, jira_filter=request.POST['jira_filter'])
        jf.save()
        return HttpResponseRedirect(reverse('jira-filter-list'))

    return render(request, 'jirafilter_form.html', locals())


class JiraFilterList(ListView):
    model = JiraFilter
    template_name = 'jirafilter_list.html'

    def get_queryset(self):
        self.user = self.request.user
        return JiraFilter.objects.filter(empl=self.user)

    def get_context_data(self, **kwargs):
        context = super(JiraFilterList, self).get_context_data(**kwargs)
        jira_list = JiraProject(user=self.request.user.username, password=self.request.session["secret"]).get_favorive_filter()
        context['jira_list'] = [(int(x.id), x.name) for x in jira_list]

        return context


class JiraFilterDetail(DetailView):
    model = JiraFilter


class JiraFilterModify(UpdateView):
    model = JiraFilter


class JiraFilterDelete(DeleteView):
    model = JiraFilter


def download_excel(request, filter_id):

    filename = excel_by_filter(filter_id=filter_id, user=request.user, passwd=request.session["secret"])
    response = HttpResponse(file(filename))
    response['Content-Type'] = 'application/vnd.ms-excel'
    response['Content-Disposition'] = 'attachment; filename=%s' % filename.split('/')[-1]
    return response
