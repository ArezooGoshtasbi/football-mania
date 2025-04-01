import requests

from football.models import Team

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

                obj, created = Team.objects.get_or_create(
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