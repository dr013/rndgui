
from django.conf.urls import url
from . import views

urlpatterns = [
    # Instances
    url(r'^instance-list$', views.InstanceList.as_view(), name='instance-list'),
    url(r'^instance-detail/(?P<pk>[0-9]+)/$', views.InstanceDetail.as_view(), name='instance-detail'),
    url(r'^instance-add/$', views.CreateInstance.as_view(), name='instance-create'),
    url(r'^instance-update/(?P<pk>[0-9]+)/$', views.UpdateInstance.as_view(), name='instance-update'),
    url(r'^instance-delete/(?P<pk>[0-9]+)/$', views.DeleteInstance.as_view(), name='instance-delete'),

]
