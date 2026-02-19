import os
import json
import base64
import requests
from datetime import datetime, timezone

# --- Environment variables ---
CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["SPOTIFY_REFRESH_TOKEN"]

# --- Step 1: Refresh access token ---
auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
auth_bytes = auth_string.encode("utf-8")
auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

token_url = "https://accounts.spotify.com/api/token"
headers = {
    "Authorization": f"Basic {auth_base64}",
    "Content-Type": "application/x-www-form-urlencoded"
}
data = {
    "grant_type": "refresh_token",
    "refresh_token": REFRESH_TOKEN
}

resp = requests.post(token_url, headers=headers, data=data)
resp.raise_for_status()
access_token = resp.json()["access_token"]

# --- Step 2: Get recently played tracks ---
recent_url = "https://api.spotify.com/v1/me/player/recently-played?limit=50"
headers = {"Authorization": f"Bearer {access_token}"}
resp = requests.get(recent_url, headers=headers)
resp.raise_for_status()
recent_data = resp.json()["items"]

# --- Step 3: Set up paths and archive ---
json_file = "recently_played.json"
archive_folder = "archive"
os.makedirs(archive_folder, exist_ok=True)

# Determine current month for archive naming
current_month = datetime.now(timezone.utc).strftime("%Y-%m")
archive_file = os.path.join(archive_folder, f"recently_played_{current_month}.json")

# --- Step 4: Load current JSON ---
if os.path.isfile(json_file):
    with open(json_file, "r") as f:
        old_items = json.load(f).get("items", [])
else:
    old_items = []

# --- Step 5: Append only new items ---
old_timestamps = set(item["played_at"] for item in old_items)
new_items = [item for item in recent_data if item["played_at"] not in old_timestamps]
all_items = old_items + new_items

# --- Step 6: Save live JSON ---
with open(json_file, "w") as f:
    json.dump({"items": all_items}, f, indent=4)

# --- Step 7: Save monthly archive ---
archive_items = []  # Always defined to avoid NameError
if new_items:
    if os.path.isfile(archive_file):
        with open(archive_file, "r") as f:
            archive_items = json.load(f).get("items", [])
    archive_items += new_items
    with open(archive_file, "w") as f:
        json.dump({"items": archive_items}, f, indent=4)

print(f"Saved {len(new_items)} new tracks. Total live JSON: {len(all_items)} tracks. Archive: {len(archive_items)} tracks.")
