from . import views
from django.conf.urls import url

urlpatterns = [
    # Product
    url(r'^admins/$', views.AdminList.as_view(), name='admin-list'),
]
