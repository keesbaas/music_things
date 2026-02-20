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


# --- Step 8: Build 30-day artist summary ---

from datetime import timedelta

cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)

# Gather all archive + live data
all_history = []

# Load monthly archive files
for file in os.listdir(archive_folder):
    if file.endswith(".json"):
        with open(os.path.join(archive_folder, file), "r") as f:
            all_history.extend(json.load(f).get("items", []))

# Also include current live JSON
all_history.extend(all_items)

artist_minutes = {}

for item in all_history:
    played_at = datetime.fromisoformat(item["played_at"].replace("Z", "+00:00"))

    if played_at >= cutoff_date:
        duration_ms = item["track"]["duration_ms"]
        minutes = duration_ms / 60000

        for artist in item["track"]["artists"]:
            name = artist["name"]
            artist_minutes[name] = artist_minutes.get(name, 0) + minutes

# Convert to sorted list
summary = sorted(
    [{"artist": k, "minutes": round(v, 2)} for k, v in artist_minutes.items()],
    key=lambda x: x["minutes"],
    reverse=True
)

# Save summary
with open("artist_30day_summary.json", "w") as f:
    json.dump(summary, f, indent=4)

print(f"Updated 30-day summary with {len(summary)} artists.")
