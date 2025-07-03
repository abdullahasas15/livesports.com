from django.contrib import admin
from .models import Tournament, Game, Team, Match

admin.site.register(Tournament)
admin.site.register(Game)
admin.site.register(Team)
admin.site.register(Match)
