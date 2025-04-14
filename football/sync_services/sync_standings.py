import requests
from football.constants import HEADERS, BASE_URL
from football.models import Season, Standing, Team

class SyncStandings:
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