from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^lobby/available/$', views.Lobby.as_view(), name='Lobby'),
]

