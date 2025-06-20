# livesports_project/apps/tournaments/models.py
from django.db import models
from django.contrib.auth.models import User # Django's built-in User model

# Define the supported games
class Game(models.Model):
    name = models.CharField(max_length=100, unique=True)
    # You might add fields like 'description', 'icon' etc. later

    class Meta:
        ordering = ['name'] # Order games alphabetically

    def __str__(self):
        return self.name

class Tournament(models.Model):
    # Link to the User (Admin) who created this tournament
    # If the User is deleted, set their tournaments' created_by to null (instead of deleting tournaments)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tournaments_created')
    
    name = models.CharField(max_length=200, unique=True)
    start_date = models.DateField()
    # Many-to-Many relationship with Game model
    # An tournament can include multiple games, and a game can be in multiple tournaments
    games = models.ManyToManyField(Game, related_name='tournaments')
    
    # You can add more fields here later, e.g., location, description, status, end_date, etc.

    class Meta:
        # Order tournaments by their start date in descending order by default
        ordering = ['-start_date', 'name']

    def __str__(self):
        return f"{self.name} (Starts: {self.start_date})"

class Team(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('tournament', 'name') # A team name must be unique within a tournament
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.tournament.name})"

class Match(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='matches_in_game')
    
    # Use ManyToManyField for teams if a match could involve more than 2 teams in some sports,
    # or if you want flexible team assignments (e.g., pairs in doubles).
    # For a simple Team A vs Team B scenario, two ForeignKey fields are often simpler.
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team1', verbose_name='Team 1')
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team2', verbose_name='Team 2')
    
    # Optional fields for score tracking (initial state)
    score_team1 = models.IntegerField(default=0)
    score_team2 = models.IntegerField(default=0)
    
    match_number = models.IntegerField(default=1) # E.g., Match 1, Match 2 within a game/tournament
    
    # You can add more fields like:
    # date_time = models.DateTimeField(null=True, blank=True)
    # venue = models.CharField(max_length=200, blank=True, null=True)
    # status = models.CharField(max_length=50, default='scheduled') # e.g., 'scheduled', 'live', 'completed'

    class Meta:
        # Order matches by game and then match number
        ordering = ['game__name', 'match_number']
        # Optionally, ensure uniqueness per match number within a game and tournament
        unique_together = ('tournament', 'game', 'match_number')

    def __str__(self):
        return f"{self.tournament.name} - {self.game.name} Match {self.match_number}: {self.team1.name} vs {self.team2.name}"
