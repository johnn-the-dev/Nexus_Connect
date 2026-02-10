# Nexus Connect

A "Looking For Group" (LFG) platform designed specifically for League of Legends players. Nexus Connect helps you find the perfect teammates based on Rank, Role, and Game Mode, featuring an integration with the Riot Games API for live player statistics.

## Status
**MVP Phase (Completed)**
The core LFG functionality and **Riot API integration** are fully implemented.
* Users can link/unlink Riot accounts.
* Live Rank & LP tracking.
* Detailed Match History with Game Mode detection.

## Purpose
I built this project to master backend development with **Python** and **Django**. The primary focus was on:
* Consuming and processing 3rd party APIs (Riot Games).
* Handling complex database relationships (Users <-> Profiles <-> LFG Posts).
* Implementing custom logic for data parsing (e.g., mapping Queue IDs to Game Modes).

*(Frontend/CSS was done by AI, since the purpose of the project was for me to learn backend development).*

## Key Features

### Riot Games API Integration
* **Secure Account Linking:** Users link accounts via Summoner Name + Tag Line. The system verifies existence and stores the unique `PUUID`.
* **Live Ranked Stats:** Fetches current Tier, Division, LP, and Wins/Losses directly from Riot servers.
* **Smart Match History:** Displays the last 10 matches with calculated details:
    * **KDA Calculator:** dynamic coloring based on performance.
    * **CS/min:** Calculates farming efficiency based on game duration.
    * **Game Mode Detection:** Uses a local JSON mapping (`queues.json`) to translate Riot's Queue IDs (e.g., `420`) into standard names like **"Ranked Solo"** or **"ARAM"**.

### LFG System
* **Dynamic Filtering:** Filter lobbies by Rank, Role, Region, or Game Mode.
* **User Management:** Full Registration, Login, and Profile management system.
* **CRUD Operations:** Users have full control to create, update, and delete their LFG posts.
* **Interactive Dashboard:** See who joined your lobby and chat with them.

## Tech Stack
* **Backend:** Python, Django 5
* **Database:** SQLite (Development default)
* **API Handling:** `requests` library
* **Environment:** `python-dotenv` for security
* **Frontend:** HTML5, CSS3, Bootstrap 5

## How to Run
1. Clone the repository.
2. Install Dependencies: `pip install -r requirements.txt`
3. Set up `.env` file in the root directory with:
   * `SECRET_KEY`
   * `RIOT_API_KEY`
   * `DEBUG=True`
4. Set up the database: `python manage.py migrate`
5. Run the server: `python manage.py runserver`