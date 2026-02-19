from langchain_core.tools import tool
from base.riot_services import get_summoner_data 

@tool
def get_lol_player_stats(game_name, tag_line, platform):
    """
    Use this tool to find stats for a League of Legends player.
    Inputs are:
    game_name: The player's name (e.g., 'Agraelus')
    tag_line: The tag without # (e.g., 'EUW')
    platform: The server ID. MUST be one of: 'euw1', 'eun1', 'na1', 'kr', 'jp1', 'tr1'. (If user says 'EUNE', convert it to 'eun1'. If 'EUW', convert to 'euw1').
    """
    try:
        data = get_summoner_data(game_name, tag_line, platform)
        
        if not data:
            return f"Error: Player {game_name}#{tag_line} on {platform} not found."

        output = []
        output.append(f"--- Stats for {data.get("game_name")}#{data.get("tag_line")} ---")
        output.append(f"Level: {data.get("level", "N/A")}")

        found_rank = False
        for key, value in data.items():
            if isinstance(value, dict) and "queueType" in value:
                q_type = value["queueType"].replace("RANKED_", "").replace("_5x5", "")
                tier = value.get("tier")
                rank = value.get("rank")
                lp = value.get("leaguePoints")
                wins = value.get("wins", 0)
                losses = value.get("losses", 0)
                total = wins + losses
                winrate = int((wins / total) * 100) if total > 0 else 0
                
                output.append(f"{q_type}: {tier} {rank} ({lp} LP) | Winrate: {winrate}% ({wins}W {losses}L)")
                found_rank = True
        
        if not found_rank:
            output.append("Rank: Unranked")

        last_games = data.get("last_games", [])
        if last_games:
            output.append(f"\n--- Last 5 Matches ({platform}) ---")
            for game in last_games[:5]: 
                champion = game.get("champion", "Unknown")
                mode = game.get("game_mode", "Unknown")

                if game.get("win"):
                    result = "VICTORY"
                else:
                    result = "DEFEAT"

                kda = game.get("kda_formatted", "0/0/0")
                cs_min = f"{game.get("cs_per_minute", 0):.1f}"
                
                output.append(f"- {result} as {champion} ({mode}): KDA {kda}, CS/min {cs_min}")
        else:
            output.append("\nNo recent match history found.")

        return "\n".join(output)

    except Exception as e:
        return f"System Error while fetching data: {str(e)}"