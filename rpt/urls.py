from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^jira-filter-list$', views.JiraFilterList.as_view(), name='jira-filter-list'),
    url(r'^jira-filter-detail/(?P<pk>[0-9]+)/$', views.JiraFilterDetail.as_view(), name='jira-filter-detail'),
    url(r'^jira-filter-add/$', views.create_filter, name='jira-filter-add'),
    url(r'^jira-filter-modify/(?P<pk>[0-9]+)/$', views.JiraFilterModify.as_view(), name='jira-filter-modify'),
    url(r'^jira-filter-delete/(?P<pk>[0-9]+)/$', views.JiraFilterDelete.as_view(), name='jira-filter-delete'),
    url(r'^jira-filter-download/(?P<filter_id>[0-9]+)/$', views.download_excel, name='download-excel'),
]

