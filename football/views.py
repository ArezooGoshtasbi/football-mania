from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse

from .models import Team, Standing, Match, Prediction, UserProfile
from football.sync_services.sync_service import SyncService
from datetime import timedelta
from django.utils import timezone



# Create your views here.
def login_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except:
            messages.error(request, "Email not found.")    
            return render(request, "football/login.html")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid password.")
            return render(request, "football/login.html")
    return render(request, "football/login.html")


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            messages.error(request, "Passwords must match.")
            return render(request, "football/register.html")
        
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            user_profile = UserProfile.objects.create(user=user)
            user_profile.save()
        except:
            messages.error(request, "Username already taken.")    
            return render(request, "football/register.html")
        login(request, user)
        return redirect("home")
    return render(request, "football/register.html")


def home(request):
    standings = Standing.objects.all().order_by("position")

    now = timezone.now()
    one_week_later = now + timedelta(days=7)

    upcoming_matches = Match.objects.filter(
        status__in=["SCHEDULED", "TIMED"], 
        utc_date__range=(now, one_week_later)
    ).order_by("utc_date")

    return render(request, "football/home.html", {
        "standings": standings,
        "upcoming_matches": upcoming_matches
    })
    

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("home"))


def sync(request):
    sync_service = SyncService()
    sync_service.sync_teams_and_players()
    season = sync_service.sync_season()
    return HttpResponse("Sync Done!")


def team(request):
    teams = Team.objects.all().values()
    return JsonResponse(list(teams), safe=False)


def sync_teams_from_file(request):
    service = SyncService()
    service.load_teams_from_file()
    return HttpResponse("Teams and players loaded from file and synced.")


def sync_season_from_file(request):
    service = SyncService()
    service.load_season_from_file()
    return HttpResponse("Season synced from file.")


def sync_matches_from_file(request):
    service = SyncService()
    service.load_matches_from_file()
    return HttpResponse("Matches  synced from file.")


def sync_standings_from_file(request):
    service = SyncService()
    service.load_standings_from_file()
    return HttpResponse("Standings  synced from file.")


@login_required
def predict_match(request, match_id):
    match = Match.objects.get(id=match_id)

    if timezone.now() > match.utc_date - timedelta(hours=2):
        messages.error(request, "Too late! You can't predict less than 2 hours before match.")
        return redirect("home")

    existing = Prediction.objects.filter(user=request.user, match=match).first()
    if existing:
        messages.error(request, " You've already predicted this match.")
        return redirect("home")
    
    if request.method == "POST":
        result = request.POST["result"]
        home_goals = int(request.POST["home_goals"])
        away_goals = int(request.POST["away_goals"])    

        if home_goals < 0 or away_goals < 0:
            messages.error(request, "Goals cannot be negative.")
            return redirect("predict", match_id=match.id)

        if result == "HOME" and home_goals <= away_goals:
            messages.error(request, "For a Home Win, home goals must be greater than away goals.")
            return redirect("predict", match_id=match.id)
        if result == "AWAY" and away_goals <= home_goals:
            messages.error(request, "For an Away Win, away goals must be greater than home goals.")
            return redirect("predict", match_id=match.id)
        if result == "DRAW" and home_goals != away_goals:
            messages.error(request, "For a Draw, goals must be equal.")
            return redirect("predict", match_id=match.id)

        Prediction.objects.create(
            user=request.user,
            match=match,
            result=result,
            home_goals=home_goals,
            away_goals=away_goals
        )
        messages.success(request, " Prediction saved successfully!")
        return redirect("home")
    return render(request, "football/predict.html", {
        "match": match
    })


@login_required
def profile_view(request):
    user = request.user
    predictions = Prediction.objects.filter(user=user)

    total_predictions = predictions.count()
    incorrect_predictions = predictions.filter(score=0, match__status="FINISHED").count()
    correct_predictions = total_predictions - incorrect_predictions


    success_rate = round((correct_predictions / total_predictions) * 100, 2) if total_predictions > 0 else 0
    has_predictions = predictions.exists()
    user_profile = UserProfile.objects.get(user=user)
    return render(request, "football/profile.html", {
        "user": user,
        "total_predictions": total_predictions,
        "correct_predictions": correct_predictions,
        "incorrect_predictions": incorrect_predictions,
        "success_rate": success_rate,
        "predictions": predictions,
        "has_predictions": has_predictions,
        "user_score": user_profile.score  
    })