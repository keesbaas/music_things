import os
import json
import base64
import requests

CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["SPOTIFY_REFRESH_TOKEN"]

# Step 1: Get new access token
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

response = requests.post(token_url, headers=headers, data=data)
token_info = response.json()

access_token = token_info["access_token"]

# Step 2: Get recently played
recent_url = "https://api.spotify.com/v1/me/player/recently-played?limit=50"

headers = {
    "Authorization": f"Bearer {access_token}"
}

response = requests.get(recent_url, headers=headers)
recent_data = response.json()

# Save JSON
with open("recently_played.json", "w") as f:
    json.dump(recent_data, f, indent=4)

print("Spotify data updated.")
