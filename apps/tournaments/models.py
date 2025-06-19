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

