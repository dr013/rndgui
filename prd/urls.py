
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^create-build/$', views.create_build, name='jira_timesheet'),
    url(r'^release-list/$', views.ReleaseList.as_view(), name='release-list'),
    url(r'^release/([\w-]+)/$', views.ProductReleaseList.as_view(), name='release-list-by-product'),
    url(r'^build/(?P<pk>[0-9]+)/$', views.ReleaseBuildList.as_view(), name='build-list-by-release'),
    url(r'^product-list$', views.ProductList.as_view(), name='product-list'),
    url(r'^product-detail/(?P<pk>[0-9]+)/$', views.ProductDetail.as_view(), name='product-detail'),
    url(r'^create-product/$', views.CreateProduct.as_view(), name='create-product'),
    url(r'build-list$', views.BuildList.as_view(), name='build-list'),
    url(r'hotfix-list$', views.HotFixList.as_view(), name='hotfix-list')
]
