
from django.conf.urls import url

from envrnmnt.views import EnvDetail
from . import views
urlpatterns = [
    # Test Env
    url(r'^test-env-list$', views.TestEnvList.as_view(), name='test-env-list'),
    url(r'^test-env-detail/(?P<pk>[0-9]+)/$', views.TestEnvDetail.as_view(), name='test-env-detail'),
    url(r'^test-env-add$', views.CreateTestEnv.as_view(), name='test-env-add'),
    url(r'^test-env-update/(?P<pk>[0-9]+)/$', views.UpdateTestEnv.as_view(), name='test-env-update'),
    url(r'^test-env-delete/(?P<pk>[0-9]+)/$', views.DeleteTestEnv.as_view(), name='test-env-delete'),
    # Env
    url(r'^env/(?P<pk>[0-9]+)/$', EnvDetail.as_view(), name='env-detail'),
    url(r'^get-one-stand$', views.acquire_env, name='get-one-stand')

]

