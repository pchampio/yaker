from django.contrib import admin
from .models import Followership
admin.autodiscover()

admin.site.register(Followership)
