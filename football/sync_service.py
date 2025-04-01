import requests
from datetime import datetime
from football.models import Team, Season

API_KEY = "7bf205ab38904c538d9c47021517f75a"

base_url = "https://api.football-data.org/v4"
headers = {
    "X-Auth-Token": API_KEY
}


class SyncService:
    def __init__(self):
        pass

    def sync_teams(self):
        url = base_url + "/competitions/PD/teams"
        response = requests.get(url, headers=headers)
        print(f"Responce recived {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            for team in data['teams']:
                name = team["name"]
                short_name = team.get("tla", "")
                logo_url = team.get("crest", "")
                id = team.get("id")

                #TO DO raise error if any of the feilds were empty

                created = Team.objects.get_or_create(
                    name=name,
                    defaults={
                        "id": id,    
                        "short_name": short_name,
                        "logo_url": logo_url
                    }
                )
                if created:
                    print(f"Created: {name}")
                else:
                    print(f"Already exists: {name}")    
        else:
            print("Error:", response.status_code)    


    def sync_season(self):
        url = base_url + "/competitions/PD"
        response = requests.get(url, headers=headers)
        print(f"Responce recived {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            # current season
            self.save_season(data.get("currentSeason"), label="Current")
            # next season (optional and may be null)
            next_season_data = data.get("seasons", [])
            if next_season_data:
                next_candidates = [s for s in next_season_data if s.get("startDate") > data.get("currentSeason", {}).get("endDate")]
                if next_candidates:
                    self.save_season(next_candidates[0], label="Next")
        else:
            print("Failed to fetch season data:", response.status_code)


    def save_season(self, season_data, label=""):
        if not season_data:
            print(f"No {label} season data found.")
            return

        start_date = season_data.get("startDate")
        end_date = season_data.get("endDate")
        winner_data = season_data.get("winner")

        if not start_date or not end_date:
            print(f"Error: {label} Season start or end date is missing.")
            return

        start_date = datetime.fromisoformat(start_date)
        end_date = datetime.fromisoformat(end_date)

        winner_team = None
        if winner_data:
            winner_id = winner_data.get("id")
            winner_team = Team.objects.filter(id=winner_id).first()

        created = Season.objects.get_or_create(
            start_date=start_date,
            end_date=end_date,
            defaults={"winner": winner_team}
        )
        if created:
            print(f"{label} Season created: {start_date.date()} to {end_date.date()}")
        else:
            print(f"{label} Season already exists: {start_date.date()} to {end_date.date()}")


            

