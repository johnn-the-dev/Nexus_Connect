# Nexus Connect 

A "Looking For Group" (LFG) website for League of Legends players. It helps you find teammates based on Rank, Role, and Game Mode.

**Status:** Project currently in MVP phase. Currently working on implementing RIOT API to connect LoL accounts and get user's LoL account statistcs.

## Purpose
I built this project to learn backend development with Python and Django. CSS, Bootstrap, JavaScript is written by AI, since this project was created for me to learn about backend in Django.

## Features
* **Filter System:** Find teammates by Rank, Role, or Mode.
* **User Accounts:** Registration and Login system.
* **CRUD:** Users can create, update, and delete their own posts.
* **Smart Logic:** Automatically handles rank requirements.

## How to Run
1. Clone the repository.
2. Install Dependencies: `pip install -r requirements.txt`
3. Set up `.env` file in the root directory with:
   * `SECRET_KEY`
   * `RIOT_API_KEY`
   * `DEBUG=True`
4. Set up the database: `python manage.py migrate`
5. Run the server: `python manage.py runserver`