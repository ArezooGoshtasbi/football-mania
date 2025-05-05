## Project Overview
Football Mania is a web-based prediction platform focused on Spain’s La Liga. Users can view upcoming matches, table standings, register , log in and predict the final score of each game before it starts. The platform calculates points automatically based on the accuracy of each prediction, and users can track their overall performance and compare it with others on a live leaderboard.
The main idea behind the project was to combine my interest in football with a fun, interactive experience that involves logic, statistics, and competition. While the core functionality is simple for users, the back-end logic includes data syncing from a real API (https://www.football-data.org), task scheduling, and status tracking — all of which make the project dynamic and realistic.

## Distinctiveness and Complexity
This application is built around real-world sports data and user prediction logic. It adds a competitive and engaging layer to the traditional football tracking experience by allowing users to predict match results and earn points based on their accuracy.

What makes the project unique and more complex is its strong focus on real-time interaction, visual design, and a personalized experience.
From a technical perspective, the project integrates data from a real football API. A custom background service (sync_service.py) was created to fetch data, update results, and calculate user scores. All of this runs automatically in the background, so users don’t notice these processes and only see the final outcome.

The syncing mechanism had to be implemented carefully. It avoids unnecessary calls and only syncs when truly needed.

To ensure the app can scale and serve many users with good performance, it tries to process as much as possible locally, without relying too much on the third-party API.
For example, after each game, it fetches the latest results and calculates variables like user scores. But when a user requests the results, the system provides its own locally stored version.

The system was designed to work independently, even if the third-party service is temporarily unavailable (due to downtime or connection issues).

Another module (seed_service.py) handles the initial loading and structuring of data. A third service (api_client.py) manages rate-limited requests and handles API communication.
The API has usage limits—such as 10 requests per minute—and delays in updating match results. To manage this, the app uses APScheduler to delay post-match sync tasks by 24 hours, helping avoid request limit issues.

## Features
* Users can register, log in, and see their personal profile.
* Upcoming La Liga matches are displayed, with details like teams and kickoff time.
* A dynamic La Liga standings table on the homepage shows team rankings, last 5 results, top 4 (UCL), and bottom 3 (relegation) teams, all with color and icon indicators.
* Users can predict the score of any upcoming match up to 2 hours before kickoff.
* Users can edit their predictions (if allowed) through a modal form without reloading the page.
* Predictions are automatically scored after the match ends, based on actual results. Each prediction is labeled as Perfect, Correct, Partial, or Incorrect based on its accuracy.
* A dynamic leaderboard shows top users based on total points and prediction accuracy. Users can sort and search through the leaderboard table.
* A fun and lightweight "Mini Chat" on the leaderboard page allows users to post short comments and cheer each other on.
* User profiles show prediction history, scores, and detailed stats with emojis and color labels. Pagination and filtering make long prediction tables easy to explore.
* Form charts display the full season match results, goals scored and conceded for top 4 teams visually.

## What’s contained in the files
Database models
### models.py
The application relies on a well-structured database schema to manage football data and user interactions. Below is a summary of the key models:
- **User**: Django’s built-in model used for authentication.
- **UserProfile**: Extends the User model with a total score field.
- **Team**: Stores team information such as name, short name, and logo URL.
- **Season**: Represents a specific La Liga season and links to the winning team.
- **Match**: Represents each match, including home/away teams, matchday, kickoff time, result, and status.
- **Standing**: Represents each team’s performance in a given season (position, points, form, etc.).
- **Prediction**: Stores each user’s prediction for a match, including predicted goals, result, and awarded score.
- **ScheduledTask**: Keeps track of background tasks for syncing or updating data using APScheduler.
- **Player**: (Optional feature) Contains basic player info like name, position, nationality, and current team.
- **Comment**: Stores user comments in the leaderboard’s Mini Chat. Each comment is serialized and shown with timestamp and ownership status.

### Endpoints
**urls.py**: Defines all the URL routes of the application. Maps each URL pattern to its corresponding view, including routes for homepage, predictions, user profile, leaderboard, charts, authentication, and API endpoints.<br>
**views.py**: Contains the core logic for rendering pages and processing user actions. Handles predictions, user profiles, leaderboard generation, form charts, authentication redirects, and AJAX endpoints such as editing predictions or posting chat comments.

### Custom types
**types.py**: Defines an enumeration (PredictionStatus) used to represent the predicted outcome of a match: Home Win, Away Win, or Draw. This enum helps enforce consistency and readability in prediction-related logic.

**constants.py**: Stores global constants used across the project, including the API base URL, request headers with the authentication token, and the current season year. This helps centralize configuration and avoid duplication.

**apps.py**: Configures the football app and ensures that scheduled background tasks (such as syncing match results and updating scores) are initialized automatically when the server starts.

**admin.py**: Registers custom models such as Team, Match, Prediction, and UserProfile to the Django admin interface, allowing administrators to view and manage football-related data directly from the admin panel.

### Templates (HTML)
**home.html**: Displays upcoming matches and the full La Liga standings table.<br>
**predict.html**: Prediction form for each match.<br>
**profile.html**: Shows user information, prediction history, and performance stats.<br>
**ranking.html**: Displays user leaderboard with live Mini Chat and filter/sort options.<br>
**form_chart.html**: Visualizes team form using Recharts.js.

### Styles (CSS)
Custom CSS files are used to style each major page and component, including navbar, home, profile, leaderboard, and charts. The styles are modular and organized by feature.

### Scripts (JavaScript)
The js/ folder contains interactive scripts used to enhance the frontend experience:<br>
**edit_prediction.js**: Opens and processes the modal to edit predictions via AJAX.<br>
**form_chart.js**: Handles the rendering of team form charts using Recharts.<br>
**home_timer.js**: Adds countdown timers for upcoming matches on the home page.<br>
**mini_chat.js**: Enables real-time comment section in the leaderboard page using AJAX.<br>
**scroll_to_top.js**: Adds a floating scroll-to-top button.<br>
**user_ranking.js**: Adds dynamic sorting and filtering for the leaderboard table.

### Images
Contains logo and team images used throughout the app, especially in the home page and prediction forms.


### Services
**api_client.py**: Handles all HTTP requests to the external football API. Manages authentication, headers, and rate-limiting to safely retrieve match and team data.<br>
**seed_service.py**: It can do two major things:
1. Dumps real and most up-to-dated data into json files. Super admin needs to do this before starting a new season (It doesn't need to be done for running the current project, I already did and placed the json files of the 2024-2025 season)
2. Loads initial data (teams, matches, standings) into the database at the start of the season or after reset. Used during setup or database refresh.<br>
**sync_service.py**: Fetches match results after games are finished and updates predictions and standings accordingly. Also creates scheduled tasks to automate result syncing and scoring.

All team and match data is retrieved from a live football API and saved to the database. Services such as api_client.py, seed_service.py, and sync_service.py are responsible for loading and updating the data dynamically. This approach allows the application to function with real data while remaining stable even if the API is unavailable.

## How to Run the Application

1. Clone the repository and navigate into the project directory:<br>
    ```
    git clone <repo-url>
    cd football-mania
    ```
2. (Optional but recommended) Create and activate a virtual environment:<br>
    ```
    python -m venv venv
    source venv/bin/activate     # On Windows: venv\Scripts\activate
    ```
3. Install dependencies:
    ```
    pip install -r requirements.txt
    ```
4. Apply database migrations:
    ```
    python manage.py migrate
    ```
5. Create a super user **(optional)**:
    ```
    python manage.py createsuperuser
    ```

6. Seed the database with real data:<br>
    Enter the shell by:
    ```
    python manage.py shell
    ```
    Then run the below lines:
    ```
    from football.sync_services.seed_service import SeedService
    seed_service = SeedService()
    seed_service.load_seed_files()
    ```
    
    After the seeding is done:
    ```
    exit()
    ```
7. Run the application:
    ```
    python manage.py runserver
    ```