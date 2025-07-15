# livesports_project/apps/tournaments/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# ------------------ Game Model ------------------
class Game(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

# ------------------ Tournament Model ------------------
class Tournament(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tournaments_created')
    name = models.CharField(max_length=200, unique=True)
    start_date = models.DateField()
    games = models.ManyToManyField(Game, related_name='tournaments')

    class Meta:
        ordering = ['-start_date', 'name']

    def __str__(self):
        return f"{self.name} (Starts: {self.start_date})"

# ------------------ Team Model ------------------
class Team(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('tournament', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.tournament.name})"

# REMOVED: Player Model (as names are typed directly now)

# ------------------ Match Model ------------------
class Match(models.Model):
    STATUS_SCHEDULED = 'scheduled'
    STATUS_LIVE = 'live'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'

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
    
    match_number = models.IntegerField(default=1)
    total_points = models.IntegerField(default=21)  # For games like Badminton

    # NEW FIELDS: Player names for Team 1 (optional)
    player1_team1 = models.CharField(max_length=100, blank=True, verbose_name='Player 1 (Team 1)')
    player2_team1 = models.CharField(max_length=100, blank=True, verbose_name='Player 2 (Team 1)')

    # NEW FIELDS: Player names for Team 2 (optional)
    player1_team2 = models.CharField(max_length=100, blank=True, verbose_name='Player 1 (Team 2)')
    player2_team2 = models.CharField(max_length=100, blank=True, verbose_name='Player 2 (Team 2)')

    points_team1 = models.IntegerField(default=0, verbose_name='Points for Team 1')
    points_team2 = models.IntegerField(default=0, verbose_name='Points for Team 2')

    # Volleyball player names for Team 1 (optional)
    volleyball_player1_team1 = models.CharField(max_length=100, blank=True, verbose_name='Volleyball Player 1 (Team 1)')
    volleyball_player2_team1 = models.CharField(max_length=100, blank=True, verbose_name='Volleyball Player 2 (Team 1)')
    volleyball_player3_team1 = models.CharField(max_length=100, blank=True, verbose_name='Volleyball Player 3 (Team 1)')
    volleyball_player4_team1 = models.CharField(max_length=100, blank=True, verbose_name='Volleyball Player 4 (Team 1)')
    volleyball_player5_team1 = models.CharField(max_length=100, blank=True, verbose_name='Volleyball Player 5 (Team 1)')
    volleyball_player6_team1 = models.CharField(max_length=100, blank=True, verbose_name='Volleyball Player 6 (Team 1)')
    # Volleyball player names for Team 2 (optional)
    volleyball_player1_team2 = models.CharField(max_length=100, blank=True, verbose_name='Volleyball Player 1 (Team 2)')
    volleyball_player2_team2 = models.CharField(max_length=100, blank=True, verbose_name='Volleyball Player 2 (Team 2)')
    volleyball_player3_team2 = models.CharField(max_length=100, blank=True, verbose_name='Volleyball Player 3 (Team 2)')
    volleyball_player4_team2 = models.CharField(max_length=100, blank=True, verbose_name='Volleyball Player 4 (Team 2)')
    volleyball_player5_team2 = models.CharField(max_length=100, blank=True, verbose_name='Volleyball Player 5 (Team 2)')
    volleyball_player6_team2 = models.CharField(max_length=100, blank=True, verbose_name='Volleyball Player 6 (Team 2)')

    # Kabaddi player names for Team 1 (optional)
    kabaddi_player1_team1 = models.CharField(max_length=100, blank=True, verbose_name='Kabaddi Player 1 (Team 1)')
    kabaddi_player2_team1 = models.CharField(max_length=100, blank=True, verbose_name='Kabaddi Player 2 (Team 1)')
    kabaddi_player3_team1 = models.CharField(max_length=100, blank=True, verbose_name='Kabaddi Player 3 (Team 1)')
    kabaddi_player4_team1 = models.CharField(max_length=100, blank=True, verbose_name='Kabaddi Player 4 (Team 1)')
    kabaddi_player5_team1 = models.CharField(max_length=100, blank=True, verbose_name='Kabaddi Player 5 (Team 1)')
    kabaddi_player6_team1 = models.CharField(max_length=100, blank=True, verbose_name='Kabaddi Player 6 (Team 1)')
    kabaddi_player7_team1 = models.CharField(max_length=100, blank=True, verbose_name='Kabaddi Player 7 (Team 1)')
    # Kabaddi player names for Team 2 (optional)
    kabaddi_player1_team2 = models.CharField(max_length=100, blank=True, verbose_name='Kabaddi Player 1 (Team 2)')
    kabaddi_player2_team2 = models.CharField(max_length=100, blank=True, verbose_name='Kabaddi Player 2 (Team 2)')
    kabaddi_player3_team2 = models.CharField(max_length=100, blank=True, verbose_name='Kabaddi Player 3 (Team 2)')
    kabaddi_player4_team2 = models.CharField(max_length=100, blank=True, verbose_name='Kabaddi Player 4 (Team 2)')
    kabaddi_player5_team2 = models.CharField(max_length=100, blank=True, verbose_name='Kabaddi Player 5 (Team 2)')
    kabaddi_player6_team2 = models.CharField(max_length=100, blank=True, verbose_name='Kabaddi Player 6 (Team 2)')
    kabaddi_player7_team2 = models.CharField(max_length=100, blank=True, verbose_name='Kabaddi Player 7 (Team 2)')

    # Throwball player names for Team 1 (optional)
    throwball_player1_team1 = models.CharField(max_length=100, blank=True, verbose_name='Throwball Player 1 (Team 1)')
    throwball_player2_team1 = models.CharField(max_length=100, blank=True, verbose_name='Throwball Player 2 (Team 1)')
    throwball_player3_team1 = models.CharField(max_length=100, blank=True, verbose_name='Throwball Player 3 (Team 1)')
    throwball_player4_team1 = models.CharField(max_length=100, blank=True, verbose_name='Throwball Player 4 (Team 1)')
    throwball_player5_team1 = models.CharField(max_length=100, blank=True, verbose_name='Throwball Player 5 (Team 1)')
    throwball_player6_team1 = models.CharField(max_length=100, blank=True, verbose_name='Throwball Player 6 (Team 1)')
    throwball_player7_team1 = models.CharField(max_length=100, blank=True, verbose_name='Throwball Player 7 (Team 1)')
    throwball_player8_team1 = models.CharField(max_length=100, blank=True, verbose_name='Throwball Player 8 (Team 1)')
    throwball_player9_team1 = models.CharField(max_length=100, blank=True, verbose_name='Throwball Player 9 (Team 1)')
    # Throwball player names for Team 2 (optional)
    throwball_player1_team2 = models.CharField(max_length=100, blank=True, verbose_name='Throwball Player 1 (Team 2)')
    throwball_player2_team2 = models.CharField(max_length=100, blank=True, verbose_name='Throwball Player 2 (Team 2)')
    throwball_player3_team2 = models.CharField(max_length=100, blank=True, verbose_name='Throwball Player 3 (Team 2)')
    throwball_player4_team2 = models.CharField(max_length=100, blank=True, verbose_name='Throwball Player 4 (Team 2)')
    throwball_player5_team2 = models.CharField(max_length=100, blank=True, verbose_name='Throwball Player 5 (Team 2)')
    throwball_player6_team2 = models.CharField(max_length=100, blank=True, verbose_name='Throwball Player 6 (Team 2)')
    throwball_player7_team2 = models.CharField(max_length=100, blank=True, verbose_name='Throwball Player 7 (Team 2)')
    throwball_player8_team2 = models.CharField(max_length=100, blank=True, verbose_name='Throwball Player 8 (Team 2)')
    throwball_player9_team2 = models.CharField(max_length=100, blank=True, verbose_name='Throwball Player 9 (Team 2)')

    status = models.CharField(max_length=20, choices=MATCH_STATUS_CHOICES, default=STATUS_SCHEDULED)
    winner = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='matches_won')

    points_history_json = models.TextField(blank=True, default='[]')

    description = models.CharField(max_length=255, blank=True, default='No description', verbose_name='Description')

    class Meta:
        ordering = ['game__name', 'match_number']
        unique_together = ('tournament', 'game', 'match_number')  # Enforce unique match_number per tournament+game for data integrity

    def __str__(self):
        # Display players if available
        players_team1 = []
        if self.player1_team1: players_team1.append(self.player1_team1)
        if self.player2_team1: players_team1.append(self.player2_team1)
        
        players_team2 = []
        if self.player1_team2: players_team2.append(self.player1_team2)
        if self.player2_team2: players_team2.append(self.player2_team2)

        team1_str = f"{self.team1.name} ({', '.join(players_team1)})" if players_team1 else self.team1.name
        team2_str = f"{self.team2.name} ({', '.join(players_team2)})" if players_team2 else self.team2.name

        return f"{self.tournament.name} - {self.game.name} Match {self.match_number}: {team1_str} vs {team2_str}"

# ------------------ UserProfile Model ------------------
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True, verbose_name="About Me")
    fav_sports = models.ManyToManyField(Game, blank=True, related_name='favorited_by_users', verbose_name="Favorite Sports")

    def __str__(self):
        return self.user.username

# ------------------ Signal to Auto-Create Profile ------------------
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    UserProfile.objects.get_or_create(user=instance)
    instance.userprofile.save()
