from django.conf.urls import include, url
from django.contrib import admin

from django.views.generic import TemplateView

urlpatterns = [
    url(r'^users/', include('users.urls')),
    url(r'^game/', include('game.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^play/', TemplateView.as_view(template_name='index.html'), name='play-client-view'),
]
