
from django.conf.urls import url

from envrnmnt.views import EnvDetail
from . import views
urlpatterns = [
    # Stands
    url(r'^test-env-list$', views.TestEnvList.as_view(), name='test-env-list'),
    url(r'^test-env-detail/(?P<pk>[0-9]+)/$', views.TestEnvDetail.as_view(), name='test-env-detail'),
    url(r'^test-env-add$', views.CreateTestEnv.as_view(), name='test-env-add'),
    url(r'^test-env-update/(?P<pk>[0-9]+)/$', views.UpdateTestEnv.as_view(), name='test-env-update'),
    url(r'^test-env-delete/(?P<pk>[0-9]+)/$', views.DeleteTestEnv.as_view(), name='test-env-delete'),
    url(r'^restapi/(?P<stand_name>[\w-]+)/$', views.rest_stand, name='stand-restapi'),
    # Env
    url(r'^env/(?P<pk>[0-9]+)/$', EnvDetail.as_view(), name='env-detail'),
    url(r'^get-one-stand$', views.acquire_stand, name='get-one-stand'),
    url(r'^release-stand/(?P<hash_code>[a-zA-Z0-9]+)$', views.release_stand_hash, name='release-stand-param'),
    url(r'^release-stand/$', views.release_stand_api, name='release-stand'),
    # UsageLog
    url(r'^usage-stand-log/(?P<stand_name>[a-zA-Z0-9-]+)$', views.UsageLogByStand.as_view(), name='usage-stand-log'),

]

