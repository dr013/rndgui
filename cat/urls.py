
from django.conf.urls import url
from . import views

urlpatterns = [
    # Test Env
    url(r'^test-env-list$', views.TestEnvList.as_view(), name='test-env-list'),
]

