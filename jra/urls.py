from django.conf.urls import url
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    url(r'^grid-demo/$', TemplateView.as_view(template_name="grid.html")),
    url(r'^grid-demo-json/$', views.json_data, name='data-json'),
]
