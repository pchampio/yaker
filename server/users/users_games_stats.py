# models

from game.models import Save
from django.db.models import Avg, Count
from datetime import date, timedelta

from django.contrib.auth.models import User
from .models import Followership

import logging
logger = logging.getLogger(__name__)

# delta de 3 jours pours les stats podium
last_day = date.today() - timedelta(days=3)

def get_last_games(user, count=10):
    return Save.objects.filter(user=user).order_by('-date')[:count]

def get_top_scores(count=3):
    response = []
    for save in Save.objects.filter(date__gte=last_day).order_by('-score')[:count]:
        response.append({"user":save.user.username, "score":save.score})
    return response

def get_worst_score():
    worst = Save.objects.filter(date__gte=last_day).order_by('score').first()
    if worst is not None:
        return {"user":worst.user.username, "score":worst.score}
    return None

def get_avg_score(user):
    avg = Save.objects.filter(
        user=user
    ).aggregate(Avg('score'))

    if avg["score__avg"] is not None:
         return round(avg['score__avg'],2)
    return None
