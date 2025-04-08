from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import Team, Standing, Match
from football.sync_service import SyncService
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
        except:
            messages.error(request, "Username already taken.")    
            return render(request, "football/register.html")
        login(request, user)
        return redirect("home")
    return render(request, "football/register.html")


@login_required
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
    if season is not None:
        sync_service.sync_matches("2025-05-15", "2025-05-25")
    # sync player
    # ...
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

