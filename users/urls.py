from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^register/$', views.CreateUser.as_view(), name='account-create'),
    url(r'^login/$', views.Login.as_view(), name='login'),
    url(r'^me/$', views.AuthUser.as_view(), name='auth-view'),
    url(r'^me/friend/add/$', views.FriendshipVue.as_view(), name='friend-add'),
    url(r'^me/friend/delete/$', views.FriendshipDell.as_view(), name='friend-delete'),
    url(r'^me/friend/$', views.FriendshipVue.as_view(), name='friend-list'),
]
