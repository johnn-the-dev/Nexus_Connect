import requests
import json
import time
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "queues.json")

load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
headers = {"X-Riot-Token": RIOT_API_KEY}

try:
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        QUEUE_DATA = json.load(f)

except FileNotFoundError:
    print("ERROR: File 'queues.json' not found.")
    QUEUE_DATA = {}

PLATFORM_TO_REGION = {
    "na1": "americas",
    "br1": "americas",
    "la1": "americas",
    "la2": "americas",
    "euw1": "europe",
    "eun1": "europe",
    "tr1": "europe",
    "ru": "europe",
    "kr": "asia",
    "jp1": "asia",
}

ERROR_CODES = {
        400: "Bad request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Data not found",
        405: "Method not allowed",
        415: "Unsupported media type",
        429: "Rate limit exceeded",
        500: "Internal server error",
        502: "Bad gateway",
        503: "Service unavailable",
        504: "Gateway timeout",
    }


def check_error(response):
    if response.status_code == 200:
        return True
    
    error_msg = ERROR_CODES.get(response.status_code, f"Unknown error {response.status_code}")
    print(f"API ERROR: {error_msg}")

    return False


def get_puuid(riot_username, tag_line, region, account_info):
    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{riot_username}/{tag_line}"
    response = requests.get(url, headers=headers)
    
    if not check_error(response):
        return

    account_info["puuid"] = response.json()["puuid"]


def get_icon_level(puuid, platform, account_info):
    url = f"https://{platform}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
    response = requests.get(url, headers=headers)

    if not check_error(response):
        return
    
    account_info["icon_id"] = response.json()["profileIconId"]
    account_info["level"] = response.json()["summonerLevel"]


def get_tier(puuid , platform, account_info):
    url = f"https://{platform}.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}"
    response = requests.get(url, headers=headers)

    if not check_error(response):
        return

    response = response.json()
    for queue in response:
        account_info[queue["queueType"]] = queue
    

def get_matchids(puuid, region, account_info, count=5):
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}"
    response = requests.get(url, headers=headers)

    if not check_error(response):
        return
    
    response = response.json()
    account_info["match_list"] = response


def get_match_info(match_id, region):
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    response = requests.get(url, headers=headers)

    if not check_error(response):
        return None

    return response.json()


def extract_player_stats(match_data, puuid):
    if not match_data:
        return None

    participants = match_data["info"]["participants"]
    queue_id = str(match_data["info"]["queueId"])
    game_mode = QUEUE_DATA.get(queue_id, "Custom")

    for participant in participants:
        if participant["puuid"] == puuid:
            cs = participant["totalMinionsKilled"] + participant["neutralMinionsKilled"]
            if match_data["info"]["gameDuration"] > 0:
                cs_per_minute = cs / (match_data["info"]["gameDuration"] / 60)
            else:
                cs_per_minute = 0

            kda_formatted = f"{participant["kills"]}/{participant["deaths"]}/{participant["assists"]}"
            if participant["deaths"] > 0:
                kda = (participant["kills"] + participant["assists"]) / participant["deaths"]
            else:
                kda = participant["kills"] + participant["assists"]

            return {
                "champion": participant["championName"],
                "kills": participant["kills"],
                "deaths": participant["deaths"],
                "assists": participant["assists"],
                "win": participant["win"],
                "lane": participant["lane"],
                "cs": participant["totalMinionsKilled"] + participant["neutralMinionsKilled"],
                "cs_per_minute": cs_per_minute,
                "kda_formatted": kda_formatted,
                "kda": kda,
                "game_mode": game_mode,
            }

    return None


def update_profile(profile):
    if not profile.puuid or not profile.platform:
        return False

    region = PLATFORM_TO_REGION.get(profile.platform)
    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-puuid/{profile.puuid}"
    response = requests.get(url, headers=headers)

    if not check_error(response):
        return False
    
    account_data = response.json()
    new_GN = account_data["gameName"]
    new_TL = account_data["tagLine"]

    if new_GN != profile.game_name or new_TL != profile.tag_line:
        profile.game_name = new_GN
        profile.tag_line = new_TL
        profile.save()
        return True

    return False


def get_summoner_data(game_name, tag_line, platform):
    region = PLATFORM_TO_REGION.get(platform)
    account_info = {
        "game_name": game_name,
        "tag_line": tag_line,
        "region": region,
        "platform": platform,
    }

    get_puuid(game_name, tag_line, region, account_info)
    if "puuid" not in account_info:
        return None

    get_icon_level(account_info["puuid"], platform, account_info)
    get_tier(account_info["puuid"], platform, account_info)
    get_matchids(account_info["puuid"], region, account_info)

    match_stats_list = []

    for match_id in account_info["match_list"]:
        full_game_data = get_match_info(match_id, region)
        if full_game_data:
            player_stats = extract_player_stats(full_game_data, account_info["puuid"])

            if player_stats:
                match_stats_list.append(player_stats)
    
    account_info["last_games"] = match_stats_list

    return account_info

def get_profile_stats(puuid, platform):
    region = PLATFORM_TO_REGION.get(platform)
    account_info = {"puuid": puuid}

    get_tier(puuid, platform, account_info)
    get_matchids(puuid, region, account_info)

    match_stats_list = []
    if "match_list" in account_info:
        for match_id in account_info["match_list"]:
            full_game_data = get_match_info(match_id, region)

            if full_game_data:
                player_stats = extract_player_stats(full_game_data, account_info["puuid"])

                if player_stats:
                    match_stats_list.append(player_stats)
    
    account_info["last_games"] = match_stats_list

    return account_info