from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^register/$', views.CreateUser.as_view(), name='account-create'),
    url(r'^login/$', views.Login.as_view(), name='login'),
    url(r'^me/$', views.AuthUser.as_view(), name='auth-view'),
    url(r'^me/notif/(?P<id>\d+)/$', views.AuthUser.as_view(), name='auth-view-del'),
    url(r'^me/follower/add/$', views.FollowershipVue.as_view(), name='follower-add'),
    url(r'^me/follower/delete/$', views.FollowershipDell.as_view(), name='follower-delete'),
    url(r'^me/follower/$', views.FollowershipVue.as_view(), name='follower-list'),
]
