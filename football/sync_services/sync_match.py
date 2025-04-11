import requests
from datetime import datetime
from football.constants import HEADERS, BASE_URL
from football.models import Team, Season, Match


class SyncMatch:
    def fetch_matches(self, dateFrom, dateTo):
        url = BASE_URL + f"/matches?competitions=2014&dateFrom={dateFrom}&dateTo={dateTo}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            return data['matches']
        else:
            print("Error:", response.status_code)
            return None


    def sync_matches(self, dateFrom, dateTo):
        matches = self.fetch_matches(dateFrom, dateTo)

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
    