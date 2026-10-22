import os
import json
import urllib.request
import urllib.error

TOKEN = os.environ["DISCORD_BOT_TOKEN"]
CHANNEL_ID = os.environ["DISCORD_CHANNEL_ID"]
SERVER = os.environ["MC_SERVER_ADDRESS"]

API_URL = f"https://api.mcsrvstat.us/3/{SERVER}"

def request_json(url, method="GET", data=None):
    headers = {"User-Agent": "MC-Discord-Status-Monitor/1.0"}
    if TOKEN and "discord.com/api/" in url:
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
        online = bool(status.get("online"))
    except Exception as exc:
        print(f"Server status check failed: {exc}")
        online = False

    message = (
        f"🟢 **Minecraft Server: ONLINE**\n"
        f"`{SERVER}`"
        if online else
        f"🔴 **Minecraft Server: OFFLINE**\n"
        f"`{SERVER}`"
    )

    base = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages"

    try:
        # Reuse the existing status message if its ID was saved.
        message_id = os.environ.get("STATUS_MESSAGE_ID", "").strip()
        if message_id:
            request_json(
                f"{base}/{message_id}",
                method="PATCH",
                data=json.dumps({"content": message}).encode()
            )
        else:
            result = request_json(
                base,
                method="POST",
                data=json.dumps({"content": message}).encode()
            )
            print("STATUS_MESSAGE_ID=" + result["id"])
    except Exception as exc:
        print(f"Discord update failed: {exc}")
        raise

if __name__ == "__main__":
    main()
