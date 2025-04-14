from football.models import Match, Prediction, UserProfile
from django.utils import timezone
from datetime import timedelta
from football.sync_services.sync_match import SyncMatch
from football.sync_services.sync_standings import SyncStandings
from football.types import PredictionStatus
from django.core.exceptions import ObjectDoesNotExist


class UpdateService:
    sync_match: SyncMatch
    sync_standings: SyncStandings

    def __init__(self):
        self.sync_match = SyncMatch()
        self.sync_standings = SyncStandings()

    
    def calculatePredictionScore(self, prediction: Prediction):
        total_score = 0
        if prediction.result == PredictionStatus.DRAW.name and prediction.match.away_score == prediction.match.home_score:
            total_score += 3
        elif prediction.result == PredictionStatus.HOME.name and prediction.match.home_score > prediction.match.away_score:
            total_score += 3
        elif prediction.result == PredictionStatus.AWAY.name and prediction.match.home_score < prediction.match.away_score:
            total_score += 3
        
        if prediction.away_goals == prediction.match.away_score:
            total_score += 1
        if prediction.home_goals == prediction.match.home_score:
            total_score += 1
        
        return total_score

    def sync_to_latest(self):
        now = timezone.now()
        two_hours_later = now - timedelta(hours=2)
        matches = Match.objects.filter(
            status__in=['TIMED', 'SCHEDULED'],
            utc_date__lte=two_hours_later  
        ).order_by('utc_date')

        for match in matches:
            print(f"{match.home_team.name} vs {match.away_team.name} | {match.status} | {match.utc_date}")
        
        if len(matches) > 0:
            standings = self.sync_standings.fetch_standings()
            self.sync_standings.update_standings(standings)
            # split the match call into 10 days chunks if needed
            match_time = matches[0].utc_date
            date_to = match_time + timedelta(days=10)
            # fetching the matches from the API
            api_matches = self.sync_match.fetch_matches(dateFrom=matches[0].utc_date.strftime("%Y-%m-%d"), dateTo=date_to.strftime("%Y-%m-%d"))
            for match in matches:
                for api_match in api_matches:
                    if match.id == api_match["id"]:
                        # Save match in DB
                        self.sync_match.save_match(api_match)
                        # Update predictions
                        predictions = Prediction.objects.filter(match=match)
                        if len(predictions) > 0:
                            for prediction in predictions:
                                new_score = self.calculatePredictionScore(prediction)
                                prediction.score = new_score
                                prediction.save()
                                try:
                                    # Update user profile
                                    user_profile = UserProfile.objects.get(user=prediction.user)
                                    if user_profile is not None:
                                        user_profile.score = user_profile.score + new_score
                                        user_profile.save()
                                    else:
                                        print("User profile not found!")
                                except ObjectDoesNotExist:
                                    print("User profile not found!")
