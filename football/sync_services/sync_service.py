import requests
import os
import json
import time
from django.conf import settings
from datetime import datetime, timedelta
from football.constants import BASE_URL, HEADERS
from football.models import Team, Season, Player, Standing
from football.sync_services.sync_match import SyncMatch
from football.sync_services.sync_standings import SyncStandings


class SyncService:
    sync_match: SyncMatch
    sync_standings: SyncStandings

    def __init__(self):
        self.sync_match = SyncMatch()
        self.sync_standings = SyncStandings()

    def sync_teams_and_players(self):
        url = BASE_URL + "/competitions/PD/teams"
        response = requests.get(url, headers=HEADERS)
        print(f"Responce recived {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            for team in data['teams']:
                db_team = self.save_team(team)
                squad = team.get("squad",[])
                for player in squad:
                    self.save_player(player, db_team)
        else:
            print("Error:", response.status_code)
    

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
        url = BASE_URL + "/competitions/PD"
        response = requests.get(url, headers=HEADERS)
        print(f"Responce recived {response.status_code}")

        season = None

        if response.status_code == 200:
            data = response.json()
            # current season
            season = self.save_season(data.get("currentSeason"))
        else:
            print("Failed to fetch season data:", response.status_code)

        return season


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

    
    def fetch_and_save_teams_to_file(self):
        url = BASE_URL + "/competitions/PD/teams"
        response = requests.get(url, headers=HEADERS)
        print(f"Responce recived {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            fixtures_path = os.path.join(settings.BASE_DIR, "fixtures")
            os.makedirs(fixtures_path, exist_ok=True)
            with open("fixtures/teams.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            print("Teams and players saved to fixtures/teams.json")    
        else:
            print("Failed to fetch teams")


    def load_teams_from_file(self):
        fixtures_path = os.path.join(settings.BASE_DIR, "fixtures", "teams.json")

        try:
            with open(fixtures_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            teams = data.get("teams", [])    
            print(f"Loaded {len(teams)} teams from file")

            for team in teams:
                db_team = self.save_team(team)
                squad = team.get("squad", [])

                for player in squad:
                    self.save_player(player, db_team)

            print("Teams and players synced from file")   

        except FileNotFoundError:
            print("File fixtures/teams.json not found.")         


    def fetch_and_save_season_to_file(self):
        url = BASE_URL + "/competitions/PD"
        response = requests.get(url, headers=HEADERS)
        print(f"Responce recived {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            current_season = data.get("currentSeason")
            if not current_season:
                print("No current season data find.")
                return
            
            fixtures_path = os.path.join(settings.BASE_DIR, "fixtures")
            os.makedirs(fixtures_path, exist_ok=True)

            file_path = os.path.join(fixtures_path, "season.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(current_season, f, ensure_ascii=False, indent=4)

            print(f"Season saved to {file_path}")    
        else:
            print("Failed fo fetch season")    


    def load_season_from_file(self):
        fixtures_path = os.path.join(settings.BASE_DIR, "fixtures", "season.json")

        try:
            with open(fixtures_path, "r", encoding="utf-8") as f:
                season_data = json.load(f)        

            season = self.save_season(season_data)    
            print("Season loaded from file and saved to DB")

        except FileNotFoundError:
            print("season.json file not found.")   


    def fetch_and_save_matches_to_file(self):
        season_year = 2024
        all_matches = []

        print(f"⚽ Fetching La Liga {season_year} matches...")

        url = BASE_URL + f"/competitions/PD/matches?season={season_year}"

        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            matches = data.get("matches", [])
            all_matches = matches

            for m in all_matches:
                if isinstance(m.get("utcDate"), datetime):
                    m["utcDate"] = m["utcDate"].isoformat()

            fixtures_path = os.path.join(settings.BASE_DIR, "fixtures")
            os.makedirs(fixtures_path, exist_ok=True)

            with open(os.path.join(fixtures_path, "matches.json"), "w", encoding="utf-8") as f:
                json.dump({"matches": all_matches}, f, ensure_ascii=False, indent=4)

            print(f"🎉 Total {len(all_matches)} matches saved to fixtures/matches.json")

        else:
            print(f"❌ Failed with status {response.status_code}")

        

    def load_matches_from_file(self):
        fixtures_path = os.path.join(settings.BASE_DIR, "fixtures", "matches.json")

        try:
            with open(fixtures_path, "r", encoding="utf-8") as f:
                data = json.load(f)     

            matches = data.get("matches", [])    
            print(f" Loaded {len(matches)} matches from file")

            for match in matches:
                self.sync_match.save_match(match)

            print("Matches synced from file")    

        except FileNotFoundError:
            print("matches.json file not found")    


    def fetch_and_save_standings_to_file(self):
        standings = self.sync_standings.fetch_standings()
    
        table = standings[0].get("table", [])

        fixtures_path = os.path.join(settings.BASE_DIR, "fixtures")
        os.makedirs(fixtures_path, exist_ok=True)

        with open(os.path.join(fixtures_path, "standings.json"), "w", encoding="utf-8") as f:
            json.dump(table, f, ensure_ascii=False, indent=4)

        print(f" Standings saved to fixtures/standings.json")



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
            
    