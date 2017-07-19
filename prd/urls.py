from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

from . import views

urlpatterns = [
    # Product
    url(r'^product-list/$', views.ProductList.as_view(), name='product-list'),
    url(r'^product-detail/(?P<pk>[0-9]+)/$', never_cache(views.ProductDetail.as_view()), name='product-detail'),
    url(r'^product-add/$', login_required(views.CreateProduct.as_view()), name='product-create'),
    url(r'^product-update/(?P<pk>[0-9]+)/$', login_required(views.UpdateProduct.as_view()), name='product-update'),
    url(r'^product-delete/(?P<pk>[0-9]+)/$', login_required(views.DeleteProduct.as_view()), name='product-delete'),
    url(r'^restapi/(?P<product>[\w-]+)/$', views.rest_product, name='product-restapi'),
    # Release
    url(r'^release-list/$', never_cache(views.ReleaseList.as_view()), name='release-list'),
    url(r'^release-detail/$', never_cache(views.ReleaseDetail.as_view()), name='release-detail'),
    url(r'^release/([\w-]+)/$', never_cache(views.ProductReleaseList.as_view()), name='release-list-by-product'),
    url(r'^release-create/(?P<product>[\w-]+)/$', never_cache(login_required(views.ReleaseCreate.as_view())),
        name='release-create'),
    url(r'^release-issue/(?P<pk>[0-9]+)/$', login_required(views.release_issue), name='release-issue'),
    # Release part
    url(r'^releasepart-add/(?P<product>[\w-]+)$', views.ReleasePartCreate.as_view(), name='releasepart-create'),
    url(r'^releasepart-update/(?P<pk>[0-9]+)/$', login_required(views.ReleasePartUpdate.as_view()),
        name='releasepart-update'),
    url(r'^releasepart-delete/(?P<pk>[0-9]+)/$', login_required(views.ReleasePartDelete.as_view()),
        name='releasepart-delete'),
    # Build
    url(r'^build/(?P<pk>[0-9]+)/$', views.ReleaseBuildList.as_view(), name='build-list-by-release'),
    url(r'^build-create/([\w-]+)/$', views.create_build, name='build-create'),
    url(r'^build-detail/(?P<pk>[0-9]+)/$', views.BuildDetail.as_view(), name='build-detail'),
    url(r'^build-list$', views.BuildList.as_view(), name='build-list'),
    # url(r'release/feeds/builds/(?P<release_id>[0-9]+)/$', views.feeds_build),
    # Hotfix
    url(r'hotfix-list$', views.HotFixList.as_view(), name='hotfix-list'),
    url(r'hotfix-create/(?P<pk>[0-9]+)/$', login_required(views.HotFixCreate.as_view()), name='hotfix-create'),
]
