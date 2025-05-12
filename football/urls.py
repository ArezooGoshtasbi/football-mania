
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login", views.login_view, name="login"),
    path("register", views.register, name="register"),
    path("logout", views.logout_view, name="logout"),
    path("sync", views.sync, name="sync"),
    path("team", views.team, name="team"),
    path("predict/<int:match_id>/", views.predict_match, name="predict"),
    path("profile/", views.profile_view, name="profile"),
    path("ranking/", views.user_ranking, name="user_ranking"),
    path("api/goals-bar-chart/", views.goals_bar_chart, name="goals_bar_chart"),
    path("form-chart/", views.form_chart_page, name="form_chart_page"),
    path("comments/", views.comments_view, name="comments"),
    path("api/match-result-pie/", views.match_result_pie, name="match_result_pie"),
    path('prediction/<int:pk>/edit/', views.edit_prediction, name='edit_prediction'),

]
