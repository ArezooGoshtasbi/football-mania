from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import Team

from football.sync_service import SyncService


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
            return redirect("index")
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
        return redirect("index")
    return render(request, "football/register.html")


@login_required
def home(request):
    return render(request, "football/home.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def index(request):
    return render(request, "football/home.html")


def sync(request):
    sync_service = SyncService()
    sync_service.sync_teams()
    return HttpResponse("Sync Done!")


def team(request):
    teams = Team.objects.all().values()
    return JsonResponse(list(teams), safe=False)