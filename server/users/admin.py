from django.contrib import admin

from .models import Followership
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from game.models import Save

from .users_games_stats import *

from django.utils.html import format_html

admin.autodiscover()

admin.site.register(Followership)

class CustomUserAdmin(UserAdmin):

    """Some more inforamtion about users games in admin panel"""

    def user_avg(self, u):
        try:
            return get_avg_score(u)
        except:
            return ''

    def user_max(self, u):
        try:
            max_s = Save.objects.filter(user=u).order_by('-score').\
                values('score','game_id').first()

            return format_html(
                '<span style="color:#80BFFF;">{}</span><br/>{}',
                str(max_s['score']) + " Pts",
                "game id :" + str(max_s['game_id'])
            )
        except:
            return ''

    def user_last_played(self, u):
        try:
            last_p = Save.objects.filter(user=u).order_by('-date').\
                values('score','date','game_id').first()
            return format_html(
                '<span style="color:#80BFFF;">{}</span><br/>{}',
                last_p['date'].strftime('%d/%m/%Y') + last_p['date'].strftime(" at %H:%M"),
                str(last_p['score']) + "  Pts on game :" + str(last_p['game_id'])
            )

        except:
            return ''

    def user_played_count(self, u):
        try:
            count = Save.objects.filter(user=u).count()
            return count

        except:
            return ''

    user_avg.short_description = 'Avg Score'
    user_played_count.short_description = 'Played Games'
    user_last_played.short_description = 'Last Game Played'
    user_max.short_description = 'Max Score'

    list_display = ("username", "email", "date_joined","is_staff",
                    'user_avg','user_max','user_last_played','user_played_count',)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
