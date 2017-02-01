from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^register/$', views.CreateUser.as_view(), name='account-create'),
    url(r'^me/$', views.AuthUser.as_view(), name='auth-view'),
    url(r'^friend/$', views.FriendshipVue.as_view(), name='friend'),
]
