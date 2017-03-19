from django.contrib import admin
from .models import Game, Save

from django.utils.html import format_html

admin.autodiscover()

#  admin.site.register(Game)
class GameAdmin(admin.ModelAdmin):
    """Display the users Save related to the game"""


    def game_total_played(self, g):
        try:
            return Save.objects.filter(game_id=g).count()
        except:
            return ''


    def game_best_player(self, g):
        try:
            user_save = Save.objects.filter(game_id=g).order_by('-score').first()
            return format_html(
                '<span style="color:#80BFFF;">{}</span><br/>{} Pts',
                user_save.user.username,
                user_save.score
            )
        except:
            return ''

    model = Game

    game_total_played.short_description = 'Total Played'
    game_best_player.short_description = 'Best Player'
    list_display = ('id', 'game_set','game_total_played',
                    'game_best_player')


admin.site.register(Game, GameAdmin)
admin.site.register(Save)
