# livesports_project/apps/tournaments/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Game(models.Model):
    name = models.CharField(max_length=100, unique=True)
    class Meta:
        ordering = ['name']
    def __str__(self):
        return self.name

class Tournament(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tournaments_created')
    name = models.CharField(max_length=200, unique=True)
    start_date = models.DateField()
    games = models.ManyToManyField(Game, related_name='tournaments')
    class Meta:
        ordering = ['-start_date', 'name']
    def __str__(self):
        return f"{self.name} (Starts: {self.start_date})"

class Team(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=100)
    class Meta:
        unique_together = ('tournament', 'name')
        ordering = ['name']
    def __str__(self):
        return f"{self.name} ({self.tournament.name})"

class Match(models.Model):
    # Match Status Choices
    STATUS_SCHEDULED = 'scheduled'
    STATUS_LIVE = 'live'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled' # Optional: for future use

    MATCH_STATUS_CHOICES = [
        (STATUS_SCHEDULED, 'Scheduled'),
        (STATUS_LIVE, 'Live'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='matches_in_game')
    
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team1', verbose_name='Team 1')
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team2', verbose_name='Team 2')
    
    score_team1 = models.IntegerField(default=0)
    score_team2 = models.IntegerField(default=0)
    total_points = models.IntegerField(default=21)  # <--- Ensure this is here
    
    match_number = models.IntegerField(default=1) 
    
    # NEW FIELDS: Status and Winner (already in your file)
    status = models.CharField(max_length=20, choices=MATCH_STATUS_CHOICES, default=STATUS_SCHEDULED)
    winner = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='matches_won')
    
    # ADD THIS CRUCIAL FIELD for points history:
    points_history_json = models.TextField(blank=True, null=True, default='[]')
    # This field will store the JSON string representation of the points history array.

    class Meta:
        ordering = ['game__name', 'match_number']
        unique_together = ('tournament', 'game', 'match_number')

    def __str__(self):
        return f"{self.tournament.name} - {self.game.name} Match {self.match_number}: {self.team1.name} vs {self.team2.name}"

# UserProfile and signals remain the same
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True, verbose_name="About Me")
    fav_sports = models.ManyToManyField(Game, blank=True, related_name='favorited_by_users', verbose_name="Favorite Sports")

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    # This ensures a UserProfile is created or retrieved for existing users without one
    # and handles saving it.
    UserProfile.objects.get_or_create(user=instance)
    instance.userprofile.save()
