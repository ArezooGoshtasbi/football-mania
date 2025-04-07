from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Team(models.Model):
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=30, blank=True)
    logo_url = models.URLField(blank=True)

    def __str__(self):
        return self.name
    

class Season(models.Model):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    winner = models.ForeignKey(Team, related_name="winner_season", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"Season {self.start_date.year} - {self.end_date.year}"


class Match(models.Model):
    season = models.ForeignKey(Season, related_name="season_matches", on_delete=models.CASCADE)
    home_team = models.ForeignKey(Team, related_name="home_matches", on_delete=models.CASCADE)
    away_team = models.ForeignKey(Team, related_name="away_matches", on_delete=models.CASCADE)
    matchday = models.IntegerField()
    utc_date = models.DateTimeField()
    status = models.CharField(max_length=20) # UP_COMING, IN_PROGRESS, FINISHED
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.home_team} vs {self.away_team} ({self.utc_date.date()})"


class Standing(models.Model):
    season = models.ForeignKey(Season, related_name="season_standings", on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    position = models.IntegerField()
    played = models.IntegerField()
    wins = models.IntegerField()
    draws = models.IntegerField()
    losses = models.IntegerField()
    points = models.IntegerField()
    form = models.CharField(max_length=9, null=True, blank=True)
    goals_for = models.IntegerField()
    goals_against = models.IntegerField()
    goal_difference = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.team.name} - {self.points} pts"


class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    predicted_home_score = models.IntegerField()
    predicted_away_score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.match}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    
    def __str__(self):
        return self.user.username
    

class ScheduledTask(models.Model):
    execution_date = models.DateTimeField() 
    executed_date = models.DateTimeField()
    status = models.CharField(max_length=30) #EXECUTED, IN_PROGRESS, NULL

    def __str__(self):
        return f"{self.execution_date} - {self.status}"
    

class Player(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=50, null=True,blank=True)
    position = models.CharField(max_length=50, null=True, blank=True)
    current_team = models.ForeignKey(Team, related_name="player", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.position})"