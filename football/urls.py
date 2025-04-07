
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("register", views.register, name="register"),
    path("logout", views.logout_view, name="logout"),
    path("sync", views.sync, name="sync"),
    path("team", views.team, name="team"),
    path("sync/teams/fromfile/", views.sync_teams_from_file, name="sync_teams_from_file"),
    path("sync/season/fromfile/", views.sync_season_from_file, name="sync_season_from_file"),
    path("sync/matches/fromfile/", views.sync_matches_from_file, name="sync_matches_from_file"),
    path("sync/standings/fromfile/", views.sync_standings_from_file, name="sync_standings_from_file"),

]
