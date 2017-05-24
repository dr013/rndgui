
from django.conf.urls import url
from . import views

urlpatterns = [
    # products
    url(r'^product-list$', views.ProductList.as_view(), name='product-list'),
    url(r'^product-detail/(?P<pk>[0-9]+)/$', views.ProductDetail.as_view(), name='product-detail'),
    url(r'^product-add/$', views.CreateProduct.as_view(), name='product-create'),
    url(r'^product-update/(?P<pk>[0-9]+)/$', views.UpdateProduct.as_view(), name='product-update'),
    url(r'^product-delete/(?P<pk>[0-9]+)/$', views.DeleteProduct.as_view(), name='product-delete'),
    # release
    url(r'^release-list/$', views.ReleaseList.as_view(), name='release-list'),
    url(r'^release-detail/$', views.ReleaseDetail.as_view(), name='release-detail'),
    url(r'^release/([\w-]+)/$', views.ProductReleaseList.as_view(), name='release-list-by-product'),

    url(r'^build/(?P<pk>[0-9]+)/$', views.ReleaseBuildList.as_view(), name='build-list-by-release'),



    url(r'build-list$', views.BuildList.as_view(), name='build-list'),
    url(r'hotfix-list$', views.HotFixList.as_view(), name='hotfix-list')
]
