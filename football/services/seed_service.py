from football.services.api_client import ApiClient
import os
import json
from django.conf import settings
from datetime import datetime
from football.models import Team, Season, Standing
from football.services.sync_service import SyncService
from football.constants import CURRENT_SEASON


class SeedService:
    def __init__(self):
        self.api_client = ApiClient()
        self.sync_service = SyncService()

    def fetch_and_save_teams_and_players_to_file(self):
       data = self.api_client.fetch_teams()
       fixtures_path = os.path.join(settings.BASE_DIR, "fixtures")
       os.makedirs(fixtures_path, exist_ok=True)
       with open("fixtures/teams.json", "w", encoding="utf-8") as f:
           json.dump(data, f, ensure_ascii=False, indent=4)
       print("Teams and players saved to fixtures/teams.json")    
    

    def fetch_and_save_season_to_file(self):
        current_season = self.api_client.fetch_season()
        fixtures_path = os.path.join(settings.BASE_DIR, "fixtures")
        os.makedirs(fixtures_path, exist_ok=True)

        file_path = os.path.join(fixtures_path, "season.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(current_season, f, ensure_ascii=False, indent=4)

        print(f"Season saved to {file_path}")

    
    def fetch_and_save_matches_to_file(self):
        season_year = CURRENT_SEASON
        all_matches = self.api_client.fetch_all_matches(season_year)

        for m in all_matches:
            if isinstance(m.get("utcDate"), datetime):
                m["utcDate"] = m["utcDate"].isoformat()

        fixtures_path = os.path.join(settings.BASE_DIR, "fixtures")
        os.makedirs(fixtures_path, exist_ok=True)

        with open(os.path.join(fixtures_path, "matches.json"), "w", encoding="utf-8") as f:
            json.dump({"matches": all_matches}, f, ensure_ascii=False, indent=4)

        print(f"🎉 Total {len(all_matches)} matches saved to fixtures/matches.json")

    
    def fetch_and_save_standings_to_file(self):
        table = self.api_client.fetch_standings()
    
        fixtures_path = os.path.join(settings.BASE_DIR, "fixtures")
        os.makedirs(fixtures_path, exist_ok=True)

        with open(os.path.join(fixtures_path, "standings.json"), "w", encoding="utf-8") as f:
            json.dump(table, f, ensure_ascii=False, indent=4)

        print(f" Standings saved to fixtures/standings.json")
    

    def create_seed_files(self):
        self.fetch_and_save_teams_and_players_to_file()
        self.fetch_and_save_season_to_file()
        self.fetch_and_save_standings_to_file()
        self.fetch_and_save_matches_to_file()
    

    def load_teams_from_file(self):
        fixtures_path = os.path.join(settings.BASE_DIR, "fixtures", "teams.json")

        try:
            with open(fixtures_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            teams = data    
            print(f"Loaded {len(teams)} teams from file")

            for team in teams:
                db_team = self.sync_service.save_team(team)
                squad = team.get("squad", [])

                for player in squad:
                    self.sync_service.save_player(player, db_team)

            print("Teams and players synced from file")   

        except FileNotFoundError:
            print("File fixtures/teams.json not found.")         


    def load_season_from_file(self):
        fixtures_path = os.path.join(settings.BASE_DIR, "fixtures", "season.json")

        try:
            with open(fixtures_path, "r", encoding="utf-8") as f:
                season_data = json.load(f)        

            season = self.sync_service.save_season(season_data)    
            print("Season loaded from file and saved to DB")

        except FileNotFoundError:
            print("season.json file not found.")   


    def load_matches_from_file(self):
        fixtures_path = os.path.join(settings.BASE_DIR, "fixtures", "matches.json")

        try:
            with open(fixtures_path, "r", encoding="utf-8") as f:
                data = json.load(f)     

            matches = data.get("matches", [])    
            print(f" Loaded {len(matches)} matches from file")

            for match in matches:
                self.sync_service.save_match(match)

            print("Matches synced from file")    

        except FileNotFoundError:
            print("matches.json file not found")    


    def load_standings_from_file(self):
        file_path = os.path.join(settings.BASE_DIR, "fixtures", "standings.json")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                table = json.load(f)

            season = Season.objects.latest("start_date")  

            Standing.objects.filter(season=season).delete()

            for item in table:
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
            print(" Standings loaded into DB from file")

        except FileNotFoundError:
            print(" standings.json not found")
            
    
    def load_seed_files(self):
        self.load_teams_from_file()
        self.load_season_from_file()
        self.load_matches_from_file()
        self.load_standings_from_file()
