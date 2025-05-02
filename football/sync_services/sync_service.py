from datetime import datetime, timedelta
from football.models import Prediction, Team, Season, Player, Standing, Match, UserProfile
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timezone
from football.sync_services.api_client import ApiClient
from django.core.exceptions import ObjectDoesNotExist
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

from football.constants import CURRENT_SEASON, PredictionStatus

def job_listener(event):
    if event.exception:
        print(f"The job crashed :(")
    else:
        print(f"The job worked fine!")


class SyncService:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        self.api_client = ApiClient()

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


    def sync_teams_and_players(self):
        teams = self.api_client.fetch_teams()
        for team in teams:
            db_team = self.save_team(team)
            squad = team.get("squad",[])
            for player in squad:
                self.save_player(player, db_team)
    

    def save_team(self, team):
        name = team["name"]
        short_name = team.get("tla", "")
        logo_url = team.get("crest", "")
        id = team.get("id")

        #TO DO raise error if any of the feilds were empty

        db_team, created = Team.objects.get_or_create(
            name=name,
            id = id,    
            short_name = short_name,
            logo_url = logo_url
        )
        if created:
            print(f"Created: {name}")
        else:
            print(f"Already exists: {name}")
        
        return db_team


    def save_player(self, player_data, team):
        player_id = player_data.get("id")
        name = player_data.get("name")
        date_of_birth = player_data.get("dateOfBirth")
        nationality = player_data.get("nationality")
        position = player_data.get("position")

        if date_of_birth:
            date_of_birth = datetime.fromisoformat(date_of_birth).date()

        if not player_id or not name:
            print("Skipping player with missing ID or name")
            return
        
        player, created = Player.objects.update_or_create(
            id=player_id,
            defaults={
                "name": name,
                "date_of_birth": date_of_birth,
                "nationality": nationality,
                "position": position,
                "current_team": team
            }
        )
        
        if created:
            print(f"Create player: {name}")

        else:
            print(f"Updated player: {name}")    


    def sync_season(self):
        return self.save_season(self.api_client.fetch_season())


    def save_season(self, season_data):
        if not season_data:
            print("No Season data found.")
            return

        start_date = season_data.get("startDate")
        end_date = season_data.get("endDate")
        id = season_data.get("id")

        if not start_date or not end_date or not id:
            print("Error: Season start or end date is missing.")
            return

        start_date = datetime.fromisoformat(start_date)
        end_date = datetime.fromisoformat(end_date)

        season ,created = Season.objects.get_or_create(
            start_date=start_date,
            end_date=end_date,
            id=id
        )

        if created:
            print(f"Season created: {start_date.date()} to {end_date.date()}")
        else:
            print(f"Season already exists: {start_date.date()} to {end_date.date()}")

        return season

    
    def run_sync(self, season_year):
        print("Running the sync ...")
        self.update_standings()
        api_matches = self.api_client.fetch_all_matches(season_year)
        print(api_matches)

        for api_match in api_matches:
            match = Match.objects.filter(id=api_match["id"]).first()
            if match.id == api_match["id"]:
                # Save match in DB
                self.save_match(api_match)
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
    

    def save_match(self, match):
        id = match["id"]
        season = Season.objects.get(id=match["season"]["id"])
        home_team = Team.objects.get(id=match["homeTeam"]["id"])
        away_team = Team.objects.get(id=match["awayTeam"]["id"])
        matchday = match["matchday"]

        utc_date_raw = match["utcDate"]
        if isinstance(utc_date_raw, str):
            utc_date = datetime.fromisoformat(utc_date_raw.replace("Z", "+00:00"))
        else:
            utc_date = utc_date_raw

        status = match["status"]
        score = match.get("score", {})
        home_score = None
        away_score = None
        if score:
            full_time = score.get("fullTime", {})
            home_score = full_time.get("home")
            away_score = full_time.get("away")

        updated_at = datetime.now()

        match, created = Match.objects.update_or_create(
            id=id,
            defaults={
                'season': season,
                'home_team': home_team,
                'away_team': away_team,
                'matchday': matchday,
                'utc_date': utc_date,
                'status': status,
                'home_score': home_score,
                'away_score': away_score,
                'updated_at': updated_at
            }
        )

        if created:
            print(f" Match created: {id}")
        else:
            print(f" Match updated: {id}")


    def update_standings(self):
        standings = self.api_client.fetch_standings()
        season = Season.objects.latest("start_date")  

        Standing.objects.filter(season=season).delete()

        for item in standings:
            team_id = item["team"]["id"]
            team = Team.objects.get(id=team_id)

            Standing.objects.create(
                season=season,
                team=team,
                position=item.get("position"),
                played=item.get("playedGames"),
                wins=item.get("won"),
                draws=item.get("draw"),
                losses=item.get("lost"),
                points=item.get("points"),
                form=item.get("form", ""),
                goals_for=item.get("goalsFor"),
                goals_against=item.get("goalsAgainst"),
                goal_difference=item.get("goalDifference"),
            )
        
        print(f"{len(standings)} Standings updated!")

    
    def create_scheduled_tasks(self):
        unfinished_matches = Match.objects.filter(
            status__in=['TIMED', 'SCHEDULED']
        ).order_by('utc_date')
        schedules = []

        should_sync = False

        for match in unfinished_matches:
            # the third party free plan has some delays for updating data
            time_plus_delay = match.utc_date + timedelta(hours=24)
            now_utc = datetime.now(timezone.utc)

            if time_plus_delay < now_utc:
                should_sync = True
                # filter similar dates
            elif match.utc_date not in schedules:
                schedules.append(match.utc_date)
                self.scheduler.add_job(
                    self.run_sync,
                    'date',
                    run_date=match.utc_date + timedelta(hours=24),
                    args=[CURRENT_SEASON],
                )
                break
        
        jobs = self.scheduler.get_jobs()
        print(f"jobs: {len(jobs)}")
        for job in jobs:
            print(job)

        self.scheduler.start()
        
        if should_sync:
            self.run_sync(season_year=CURRENT_SEASON)
