# Generated by Django 5.2.3 on 2025-07-11 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0007_match_throwball_player1_team1_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='kabaddi_player1_team1',
            field=models.CharField(blank=True, max_length=100, verbose_name='Kabaddi Player 1 (Team 1)'),
        ),
        migrations.AddField(
            model_name='match',
            name='kabaddi_player1_team2',
            field=models.CharField(blank=True, max_length=100, verbose_name='Kabaddi Player 1 (Team 2)'),
        ),
        migrations.AddField(
            model_name='match',
            name='kabaddi_player2_team1',
            field=models.CharField(blank=True, max_length=100, verbose_name='Kabaddi Player 2 (Team 1)'),
        ),
        migrations.AddField(
            model_name='match',
            name='kabaddi_player2_team2',
            field=models.CharField(blank=True, max_length=100, verbose_name='Kabaddi Player 2 (Team 2)'),
        ),
        migrations.AddField(
            model_name='match',
            name='kabaddi_player3_team1',
            field=models.CharField(blank=True, max_length=100, verbose_name='Kabaddi Player 3 (Team 1)'),
        ),
        migrations.AddField(
            model_name='match',
            name='kabaddi_player3_team2',
            field=models.CharField(blank=True, max_length=100, verbose_name='Kabaddi Player 3 (Team 2)'),
        ),
        migrations.AddField(
            model_name='match',
            name='kabaddi_player4_team1',
            field=models.CharField(blank=True, max_length=100, verbose_name='Kabaddi Player 4 (Team 1)'),
        ),
        migrations.AddField(
            model_name='match',
            name='kabaddi_player4_team2',
            field=models.CharField(blank=True, max_length=100, verbose_name='Kabaddi Player 4 (Team 2)'),
        ),
        migrations.AddField(
            model_name='match',
            name='kabaddi_player5_team1',
            field=models.CharField(blank=True, max_length=100, verbose_name='Kabaddi Player 5 (Team 1)'),
        ),
        migrations.AddField(
            model_name='match',
            name='kabaddi_player5_team2',
            field=models.CharField(blank=True, max_length=100, verbose_name='Kabaddi Player 5 (Team 2)'),
        ),
        migrations.AddField(
            model_name='match',
            name='kabaddi_player6_team1',
            field=models.CharField(blank=True, max_length=100, verbose_name='Kabaddi Player 6 (Team 1)'),
        ),
        migrations.AddField(
            model_name='match',
            name='kabaddi_player6_team2',
            field=models.CharField(blank=True, max_length=100, verbose_name='Kabaddi Player 6 (Team 2)'),
        ),
        migrations.AddField(
            model_name='match',
            name='kabaddi_player7_team1',
            field=models.CharField(blank=True, max_length=100, verbose_name='Kabaddi Player 7 (Team 1)'),
        ),
        migrations.AddField(
            model_name='match',
            name='kabaddi_player7_team2',
            field=models.CharField(blank=True, max_length=100, verbose_name='Kabaddi Player 7 (Team 2)'),
        ),
    ]
