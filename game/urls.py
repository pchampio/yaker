from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^playsolo/$', views.PlaySolo.as_view(), name='playsolo'),
]

