import requests
from datetime import datetime
from football.models import Team, Season, Match, Player


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

