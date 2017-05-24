
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^create_build/$', views.create_build, name='jira_timesheet'),
    url(r'^release-list$', views.ReleaseList.as_view(), name='release-list'),
    url(r'^build/([\w-]+)/$', views.ReleaseBuildList.as_view()),
    url(r'^product-list$', views.ProductList.as_view(), name='product-list'),
    url(r'build-list$', views.BuildList.as_view(), name='build-list'),
    url(r'hotfix-list$', views.HotFixList.as_view(), name='hotfix-list')
]
