from football.models import Match, Prediction, UserProfile
from django.utils import timezone
from datetime import timedelta, datetime

from football.sync_services.sync_match import SyncMatch
from football.types import PredictionStatus
from django.core.exceptions import ObjectDoesNotExist


class UpdateService:
    sync_match: SyncMatch

    def __init__(self):
        self.sync_match = SyncMatch()

    
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
        # split the match call into 10 days chunks if needed
            # dt_utc = datetime.fromtimestamp(matches[0].utc_date, tz=timezone.utc)
            # print("**********************")
            # formatted = dt_utc.strftime("%Y-%m-%d %H:%M:%S %Z")
            match_time = matches[0].utc_date
            date_to = match_time + timedelta(days=10)
            api_matches = self.sync_match.fetch_matches(dateFrom=matches[0].utc_date.strftime("%Y-%m-%d"), dateTo=date_to.strftime("%Y-%m-%d"))
            print(api_matches)
            for match in matches:
                for api_match in api_matches:
                    if match.id == api_match["id"]:
                        print("BOOOOOOOOOOOOOOOOOOOOM!!!!!!!")
                        self.sync_match.save_match(api_match)
                        predictions = Prediction.objects.filter(match=match)
                        if len(predictions) > 0:
                            print("Prediction found!")
                            print(len(predictions))
                            for prediction in predictions:
                                new_score = self.calculatePredictionScore(prediction)
                                print("NEW SCORE")
                                print(new_score)
                                prediction.score = new_score
                                prediction.save()
                                try:
                                    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                                    print(prediction.user.id)
                                    user_profile = UserProfile.objects.get(user=prediction.user)
                                    if user_profile is not None:
                                        print("NEW UserProfile")
                                        print(user_profile.score)
                                        user_profile.score = user_profile.score + new_score
                                        print(user_profile.score)
                                        user_profile.save()
                                    else:
                                        print("User profile not found!")
                                except ObjectDoesNotExist:
                                    print("User profile not found!")

        # update the DB --> stading