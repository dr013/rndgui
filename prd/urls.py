
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^create_build/$', views.create_build, name='jira_timesheet'),
    url(r'^$', views.ReleaseList.as_view()),
]
