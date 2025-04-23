from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db.models import Sum
import json
from .models import Team, Standing, Match, Prediction, UserProfile, Comment
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
    finished_predictions = predictions.filter(match__status="FINISHED")
    
    total_finished = finished_predictions.count()
    correct_predictions = finished_predictions.filter(score=3).count()
    correct_result = finished_predictions.filter(score=3).count()
    partially_correct = finished_predictions.filter(score__in=[1, 2]).count()
    incorrect_predictions = finished_predictions.filter(score=0).count()
    total_score = finished_predictions.aggregate(total=Sum("score"))["total"] or 0
    max_possible_score = total_finished * 5
    success_rate = round((total_score / max_possible_score) * 100, 2) if total_finished > 0 else 0

    has_predictions = predictions.exists()
    user_profile = UserProfile.objects.get(user=user)

    return render(request, "football/profile.html", {
        "user": user,
        "total_predictions": total_predictions,
        "correct_predictions": correct_predictions,
        "correct_result": correct_result,
        "partially_correct": partially_correct,
        "incorrect_predictions": incorrect_predictions,
        "success_rate": success_rate,
        "predictions": predictions,
        "has_predictions": has_predictions,
        "user_score": user_profile.score,
        "total_finished": total_finished
    })


def user_ranking(request):
    user_profiles = UserProfile.objects.select_related("user").all()
    ranking_data = []
    total_predictions_count = 0
    total_points = 0
    top_accuracy = {"username": "-", "accuracy": 0}
    highest_accuracy = 0
    top_user = None

    for profile in sorted(user_profiles, key=lambda x: x.score, reverse=True):
        user = profile.user
        user_predictions = Prediction.objects.filter(
            user=user,
            match__status="FINISHED",
            score__isnull=False
        )
        total_finished = user_predictions.count()

        if total_finished == 0:
            continue

        total_predictions_count += total_finished
        total_points += profile.score

        max_possible_score = total_finished * 5
        performance = round((profile.score / max_possible_score) * 100, 2) if max_possible_score > 0 else 0

        perfect_predictions = user_predictions.filter(score=5).count()
        accuracy = round((perfect_predictions / total_finished) * 100, 2)

        if accuracy > highest_accuracy:
            highest_accuracy = accuracy
            top_accuracy = {
                "username": user.username,
                "accuracy": accuracy
            }

        ranking_data.append({
            "rank": len(ranking_data) + 1,
            "username": user.username,
            "score": profile.score,
            "performance": performance,
            "total_finished": total_finished,
            "is_current_user": user == request.user
        })
    if ranking_data:
        top_user = max(ranking_data, key=lambda x: x["score"])

    return render(request, "football/user_ranking.html", {
        "ranking_data": ranking_data,
        "total_users": len(ranking_data),
        "total_predictions": total_predictions_count,
        "top_user": top_user,
        "top_accuracy": top_accuracy,
        "total_points": total_points
    })


@csrf_exempt
@require_http_methods(["GET", "POST"])
def comments_view(request):
    if request.method == "GET":
        comments = Comment.objects.order_by('-timestamp')[:50]
        return JsonResponse([c.serialize(current_user=request.user) for c in comments], safe=False)
    
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Login required"}, status=401)
    
    data = json.loads(request.body)
    message = data.get("message")
    if not message:
        return JsonResponse({"error": "Empty message"}, status=400)
    
    comment = Comment(user=request.user, message=message)
    comment.save()
    return JsonResponse(comment.serialize(), status=201)
