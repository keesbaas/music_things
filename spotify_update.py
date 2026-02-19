import os
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("SPOTIFY_REFRESH_TOKEN")
REDIRECT_URI = "http://localhost:8888/callback"

scope = "user-read-recently-played"

auth_manager = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=scope
)

token_info = auth_manager.refresh_access_token(REFRESH_TOKEN)

sp = spotipy.Spotify(auth=token_info['access_token'])

results = sp.current_user_recently_played(limit=50)

with open("recently_played.json", "w") as f:
    json.dump(results, f, indent=4)

print("Saved recently played tracks.")
