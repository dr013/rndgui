
from django.conf.urls import url
from . import views

urlpatterns = [
    # DBInstances
    url(r'^dbinstance-list$', views.DBInstanceList.as_view(), name='dbinstance-list'),
    url(r'^dbinstance-detail/(?P<pk>[0-9]+)/$', views.DBInstanceDetail.as_view(), name='dbinstance-detail'),
    url(r'^dbinstance-add/$', views.CreateDBInstance.as_view(), name='dbinstance-create'),
    url(r'^dbinstance-update/(?P<pk>[0-9]+)/$', views.UpdateDBInstance.as_view(), name='dbinstance-update'),
    url(r'^dbinstance-delete/(?P<pk>[0-9]+)/$', views.DeleteDBInstance.as_view(), name='dbinstance-delete'),

    #   WEBInstances
    url(r'^webinstance-list$', views.WEBInstanceList.as_view(), name='webinstance-list'),
    url(r'^webinstance-detail/(?P<pk>[0-9]+)/$', views.WEBInstanceDetail.as_view(), name='webinstance-detail'),
    url(r'^webinstance-add/$', views.CreateWEBInstance.as_view(), name='webinstance-create'),
    url(r'^webinstance-update/(?P<pk>[0-9]+)/$', views.UpdateWEBInstance.as_view(), name='webinstance-update'),
    url(r'^webinstance-delete/(?P<pk>[0-9]+)/$', views.DeleteWEBInstance.as_view(), name='webinstance-delete'),

    #   STLNInstances
    url(r'^stlninstance-list$', views.STLNInstanceList.as_view(), name='stlninstance-list'),
    url(r'^stlninstance-detail/(?P<pk>[0-9]+)/$', views.STLNInstanceDetail.as_view(), name='stlninstance-detail'),
    url(r'^stlninstance-add/$', views.CreateSTLNInstance.as_view(), name='stlninstance-create'),
    url(r'^stlninstance-update/(?P<pk>[0-9]+)/$', views.UpdateSTLNInstance.as_view(), name='stlninstance-update'),
    url(r'^stlninstance-delete/(?P<pk>[0-9]+)/$', views.DeleteSTLNInstance.as_view(), name='stlninstance-delete'),

    #   Environments
    url(r'^env-list$', views.EnvLint.as_view(), name='env-list'),
    url(r'^env-detail/(?P<pk>[0-9]+)/$', views.EnvDetail.as_view(), name='env-detail'),
    url(r'^env-add/$', views.CreateEnv, name='env-create'),
    url(r'^env-update/(?P<pk>[0-9]+)/$', views.UpdateEnv, name='env-update'),
    url(r'^env-delete/(?P<pk>[0-9]+)/$', views.DeleteEnv.as_view(), name='env-delete'),
]

