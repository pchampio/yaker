from django.contrib import admin
from .models import Game, Save
admin.autodiscover()

admin.site.register(Game)
admin.site.register(Save)
