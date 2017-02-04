from django.contrib import admin
from .models import Friendship
admin.autodiscover()

admin.site.register(Friendship)
