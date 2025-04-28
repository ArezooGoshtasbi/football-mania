from datetime import datetime
from football.constants import BASE_URL, HEADERS
from football.models import Team, Season, Player, Standing, Match, ScheduledTask
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from django.utils import timezone


class SyncService:
    def __init__(self):
        self.scheduler = BackgroundScheduler()


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


    
    def sync_matches(self, dateFrom, dateTo):
        matches = self.api_client.fetch_season(dateFrom, dateTo)

        if matches is not None:
            for match in matches:
                self.save_match(match)
        else:
            print("No Match Was Saved!")
    

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


    def sync_matches_wrapper(self, task_id, date_from, date_to):
        task = ScheduledTask.objects.get(id=task_id)
        task.attempt += 1
        task.updated_at = timezone.now()
        task.save()

        try:
            self.sync_matches(date_from, date_to)

            task.status = 'done'
            task.save()

        except Exception as e:
            print(f"Task {task.name} failed: {e}")
            task.save()


    def schedule_pending_tasks(self):
        now = timezone.now()
        pending_tasks = ScheduledTask.objects.filter(status='scheduled')

        for task in pending_tasks:
            run_time = task.run_at
            payload = task.payload or {}  # assuming payload has dateFrom and dateTo

            date_from = payload.get('dateFrom')
            date_to = payload.get('dateTo')

            if not date_from or not date_to:
                print(f"Task {task.id} missing required parameters. Skipping.")
                continue

            if run_time <= now:
                # If the time already passed, execute immediately
                self.sync_matches_wrapper(task.id, date_from, date_to)
            else:
                # Schedule for future
                self.scheduler.add_job(
                    self.sync_matches_wrapper,
                    'date',
                    run_date=run_time,
                    args=[task.id, date_from, date_to]
                )

        self.scheduler.start()
    

    def update_standings(self, standings):
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