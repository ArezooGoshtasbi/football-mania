
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login", views.login_view, name="login"),
    path("register", views.register, name="register"),
    path("logout", views.logout_view, name="logout"),
    path("sync", views.sync, name="sync"),
    path("team", views.team, name="team"),
    path("sync/teams/fromfile/", views.sync_teams_from_file, name="sync_teams_from_file"),
    path("sync/season/fromfile/", views.sync_season_from_file, name="sync_season_from_file"),
    path("sync/matches/fromfile/", views.sync_matches_from_file, name="sync_matches_from_file"),
    path("sync/standings/fromfile/", views.sync_standings_from_file, name="sync_standings_from_file"),
    path("predict/<int:match_id>/", views.predict_match, name="predict"),
    path("profile/", views.profile_view, name="profile"),
    path("ranking/", views.user_ranking, name="user_ranking"),
    path("comments/", views.comments_view, name="comments"),
    path("form-chart/", views.form_chart_page, name="form_chart_page"),
    path("api/form-chart/", views.form_chart, name="form_chart"),

]
