import requests
from football.constants import HEADERS, BASE_URL


class ApiClient:
    """This class is reponsible for interacting with the third-party API and map the data to be consumed in our application"""
    def fetch_standings(self):
        url = BASE_URL + "/competitions/PD/standings"
        response = requests.get(url, headers=HEADERS)
        print(f" Standings response: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            standings = data.get("standings", [])  
            if standings and len(standings) > 0:
                return standings[0].get("table", [])

        return None


    def fetch_matches(self, dateFrom, dateTo):
        url = BASE_URL + f"/matches?competitions=2014&dateFrom={dateFrom}&dateTo={dateTo}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            return data['matches']
        else:
            print("Error:", response.status_code)
            return None


    def fetch_all_matches(self, season_year):
        print(f"⚽ Fetching La Liga {season_year} matches...")
        url = BASE_URL + f"/competitions/PD/matches?season={season_year}"

        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            matches = data.get("matches", [])
            return matches
        else:
            print(f"❌ Failed with status {response.status_code}")
            return None
    

    def fetch_teams(self):
        url = BASE_URL + "/competitions/PD/teams"
        response = requests.get(url, headers=HEADERS)
        print(f"Responce recived {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            return data['teams']
        else:
            print("Error:", response.status_code)
            return None


    def fetch_season(self):
        url = BASE_URL + "/competitions/PD"
        response = requests.get(url, headers=HEADERS)
        print(f"Responce recived {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            return data.get("currentSeason")
        else:
            print("Failed to fetch season data:", response.status_code)
            return None
