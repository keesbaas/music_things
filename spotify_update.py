import os
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8888/callback"

scope = "user-read-recently-played"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=scope
))

results = sp.current_user_recently_played(limit=50)

with open("recently_played.json", "w") as f:
    json.dump(results, f, indent=4)

print("Saved recently played tracks.")
