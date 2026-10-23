
import os
import json
import socket
import urllib.request
import urllib.error

TOKEN = os.environ["DISCORD_BOT_TOKEN"]
CHANNEL_ID = os.environ["DISCORD_CHANNEL_ID"]
SERVER = os.environ["MC_SERVER_ADDRESS"]
MESSAGE_ID = os.environ.get("STATUS_MESSAGE_ID", "").strip()


def check_server():
    try:
        host, port = SERVER.rsplit(":", 1) if ":" in SERVER else (SERVER, "25565")
        port = int(port)

        with socket.create_connection((host, port), timeout=5):
            return True
    except Exception as exc:
        print(f"Minecraft server not reachable: {exc}")
        return False


def discord_request(url, method="GET", data=None):
    headers = {
        "Authorization": f"Bot {TOKEN}",
        "User-Agent": "MC-Status-Monitor/1.0",
    }
    if data is not None:
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(
        url, data=data, headers=headers, method=method
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        body = response.read()
        return json.loads(body) if body else {}


def main():
    online = check_server()

    message = (
        f"🟢 **Minecraft Server: ONLINE**\n`{SERVER}`"
        if online else
        f"🔴 **Minecraft Server: OFFLINE / SLEEP / QUEUED**\n`{SERVER}`"
    )

    base = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages"
    payload = json.dumps({"content": message}).encode()

    if MESSAGE_ID:
        discord_request(f"{base}/{MESSAGE_ID}", "PATCH", payload)
    else:
        result = discord_request(base, "POST", payload)
        print("STATUS_MESSAGE_ID=" + result["id"])


if __name__ == "__main__":
    main()
