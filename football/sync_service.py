import requests
import os
import json
import time
from django.conf import settings
from datetime import datetime, timedelta
from football.models import Team, Season, Match, Player, Standing


API_KEY = "7bf205ab38904c538d9c47021517f75a"

base_url = "https://api.football-data.org/v4"
headers = {
    "X-Auth-Token": API_KEY
}


class SyncService:
    def __init__(self):
        pass

    def sync_teams_and_players(self):
        url = base_url + "/competitions/PD/teams"
        response = requests.get(url, headers=headers)
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
        url = base_url + "/competitions/PD"
        response = requests.get(url, headers=headers)
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


    def sync_matches(self, dateFrom, dateTo):
        url = base_url + f"/matches?competitions=2014&dateFrom={dateFrom}&dateTo={dateTo}"
        response = requests.get(url, headers=headers)
        print(f"Responce recived {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            for match in data['matches']:
                self.save_match(match)
        else:
            print("Error:", response.status_code)
    

    def save_match(self, match):
        id = match["id"]
        print(match["season"]["id"])
        season = Season.objects.get(id=match["season"]["id"])
        print(season)
        home_team = Team.objects.get(id=match["homeTeam"]["id"])
        print(home_team)
        away_team = Team.objects.get(id=match["awayTeam"]["id"])
        print(away_team)
        matchday = match["matchday"]
        utc_date = datetime.fromisoformat(match["utcDate"].replace("Z", "+00:00"))
        status = match["status"]
        score = match["score"]
        if score is not None:
            home_score = match["score"]["fullTime"]["home"]
            away_score = match["score"]["fullTime"]["away"]
        updated_at = datetime.now()
        

        # TODO raise error if any of the feilds were empty

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
            print(f"Match created: {id}")
        else:
            print(f"Match already exists: {id}")


    def fetch_and_save_teams_to_file(self):
        url = base_url + "/competitions/PD/teams"
        response = requests.get(url, headers=headers)
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
        url = base_url + "/competitions/PD"
        response = requests.get(url, headers=headers)
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

        fixtures_path = os.path.join(settings.BASE_DIR, "fixtures")
        os.makedirs(fixtures_path, exist_ok=True)

        progress_file_path = os.path.join(fixtures_path, "matches_progress.txt")

        if os.path.exists(progress_file_path):
            with open(progress_file_path, "r") as f:
                start_date_str = f.read().strip()
                start_date = datetime.fromisoformat(start_date_str)
                print(f" Resuming from: {start_date.date()}")
        else:
            start_date = datetime(season_year, 8, 1)
            print(f" Starting from beginning: {start_date.date()}")

        end_date = datetime(season_year + 1, 6, 1)
        current = start_date

        print(f" Fetching La Liga {season_year}-{season_year + 1} matches...")

        while current < end_date:
            date_from = current.strftime("%Y-%m-%d")
            date_to = (current + timedelta(days=5)).strftime("%Y-%m-%d")

            url = base_url + f"/matches?competitions=2014&dateFrom={date_from}&dateTo={date_to}"
            response = requests.get(url, headers=headers)
            print(f" {date_from} to {date_to} → {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                matches = data.get("matches", [])
                all_matches.extend(matches)

                with open(progress_file_path, "w") as progress_file:
                    progress_file.write(date_to)
                print(f" Progress saved: {date_to}")
            else:
                print(f" Failed for range {date_from} to {date_to}")
                break 

            current += timedelta(days=6)
            time.sleep(6)  

        with open(os.path.join(fixtures_path, "matches.json"), "w", encoding="utf-8") as f:
            json.dump({"matches": all_matches}, f, ensure_ascii=False, indent=4)

        print(f" Total {len(all_matches)} matches saved to fixtures/matches.json")   


    def load_matches_from_file(self):
        fixtures_path = os.path.join(settings.BASE_DIR, "fixtures", "matches.json")

        try:
            with open(fixtures_path, "r", encoding="utf-8") as f:
                data = json.load(f)     

            matches = data.get("matches", [])    
            print(f" Loaded {len(matches)} matches from file")

            for match in matches:
                self.save_match(match)

            print("Matches synced from file")    

        except FileNotFoundError:
            print("matches.json file not found")    


    def fetch_and_save_standings_to_file(self):
        url = base_url + "/competitions/PD/standings"
        response = requests.get(url, headers=headers)
        print(f" Standings response: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            standings = data.get("standings", [])  

            if not standings:
                print(" No standings found in response")
                return
            
            table = standings[0].get("table", [])

            fixtures_path = os.path.join(settings.BASE_DIR, "fixtures")
            os.makedirs(fixtures_path, exist_ok=True)

            with open(os.path.join(fixtures_path, "standings.json"), "w", encoding="utf-8") as f:
                json.dump(table, f, ensure_ascii=False, indent=4)

            print(f" Standings saved to fixtures/standings.json")
        else:
            print(" Failed to fetch standings")


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
            