
import os
import json
import urllib.request
import urllib.error

TOKEN = os.environ["DISCORD_BOT_TOKEN"]
CHANNEL_ID = os.environ["DISCORD_CHANNEL_ID"]
SERVER = os.environ["MC_SERVER_ADDRESS"]
MESSAGE_ID = os.environ.get("STATUS_MESSAGE_ID", "").strip()

API_URL = f"https://api.mcsrvstat.us/3/{SERVER}"


def request_json(url, method="GET", data=None):
    headers = {
        "User-Agent": "MC-Player-Monitor/1.0",
        "Authorization": f"Bot {TOKEN}",
    }
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
        req = urllib.request.Request(
            API_URL,
            headers={"User-Agent": "MC-Player-Monitor/1.0"}
        )
        with urllib.request.urlopen(req, timeout=20) as response:
            status = json.loads(response.read().decode())

        players = status.get("players", {})
        online_count = players.get("online", 0)
        names = players.get("list", [])

        if names:
            player_text = "\n".join(f"• {p['name'] if isinstance(p, dict) else p}" for p in names)
        else:
            player_text = "Kono player-er naam API-te paoa jayni."

        message = (
            f"👥 **Minecraft Players: {online_count}**\n"
            f"**Player Names:**\n{player_text}\n"
            f"🌐 `{SERVER}`"
        )

    except Exception as exc:
        print(f"Player check failed: {exc}")
        message = (
            f"👥 **Minecraft Player Status**\n"
            f"Player information ekhon paoa jacche na.\n"
            f"🌐 `{SERVER}`"
        )

    base = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages"
    payload = json.dumps({"content": message}).encode()

    if MESSAGE_ID:
        request_json(f"{base}/{MESSAGE_ID}", "PATCH", payload)
    else:
        result = request_json(base, "POST", payload)
        print("STATUS_MESSAGE_ID=" + result["id"])


if __name__ == "__main__":
    main()
