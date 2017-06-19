

from django.conf.urls import url, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from acm.views import start, logout_view, login_view


urlpatterns = [
    url(r'^$', start, name='start'),
    url(r'^admin_tools/', include('admin_tools.urls')),
    url(r'^product/', include('prd.urls')),
    url(r'^instance/', include('envrnmnt.urls')),
    url(r'^test-env/', include('cat.urls')),
    url(r'^login/', login_view, name='login'),
    url(r'^logout/', logout_view, name='logout'),
    url(r'^admin/', admin.site.urls),
    url(r'^jra/', include('jra.urls')),
    url(r'^acm/', include('acm.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
