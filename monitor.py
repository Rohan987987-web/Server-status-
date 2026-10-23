
import os
import json
import urllib.request
import urllib.error

TOKEN = os.environ["DISCORD_BOT_TOKEN"]
CHANNEL_ID = os.environ["DISCORD_CHANNEL_ID"]
SERVER = os.environ["MC_SERVER_ADDRESS"]
MESSAGE_ID = os.environ.get("STATUS_MESSAGE_ID", "").strip()

API_URL = f"https://api.mcstatus.io/v2/status/java/{SERVER}"


def request_json(url, method="GET", data=None, discord=False):
    headers = {"User-Agent": "Minecraft-Player-Monitor/1.0"}

    if discord:
        headers["Authorization"] = f"Bot {TOKEN}"

    if data is not None:
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(
        url, data=data, headers=headers, method=method
    )

    with urllib.request.urlopen(req, timeout=20) as response:
        body = response.read()
        return json.loads(body) if body else {}


def main():
    try:
        status = request_json(API_URL)

        players = status.get("players") or {}
        online_count = players.get("online", 0)
        names = players.get("list") or players.get("sample") or []

        player_names = []

        for player in names:
            if isinstance(player, dict):
                name = player.get("name_clean") or player.get("name")
                if name:
                    player_names.append(str(name))
            elif player:
                player_names.append(str(player))

        if player_names:
            player_text = "\n".join(
                f"• {name}" for name in player_names
            )
        else:
            player_text = "Player names API-te paoa jayni."

        message = (
            f"👥 **Players Online: {online_count}**\n"
            f"**Player Names:**\n{player_text}\n"
            f"🌐 `{SERVER}`"
        )

    except Exception as exc:
        print(f"Player API error: {exc}")
        message = (
            f"👥 **Player Status**\n"
            f"Player information ekhon paoa jacche na.\n"
            f"🌐 `{SERVER}`"
        )

    base = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages"
    payload = json.dumps({"content": message}).encode("utf-8")

    try:
        if MESSAGE_ID:
            request_json(
                f"{base}/{MESSAGE_ID}",
                method="PATCH",
                data=payload,
                discord=True
            )
            print("Discord status message updated.")
        else:
            result = request_json(
                base,
                method="POST",
                data=payload,
                discord=True
            )
            print("STATUS_MESSAGE_ID=" + result["id"])

    except urllib.error.HTTPError as exc:
        print("Discord error:", exc.code)
        print(exc.read().decode("utf-8", errors="replace"))
        raise


if __name__ == "__main__":
    main()
