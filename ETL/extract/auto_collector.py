import json
import time
import requests
import os

from dotenv import load_dotenv
from pathlib import Path
from common.normalize import normalize

load_dotenv()
API_KEY = os.getenv("LASTFM")
BASE_DIR = Path(__file__).resolve().parent.parent
SEEN_ARTISTS= BASE_DIR / "data" / "extract" / "seen_artists.json"
SEEN_TRACKS = BASE_DIR / "data" / "extract" / "seen_tracks.json"
NEW_TRACKS = BASE_DIR / "data" / "extract" / "new_track.json"


def load():
    with open(SEEN_ARTISTS, "r", encoding="utf-8") as seen_artists,\
    open(SEEN_TRACKS, "r", encoding="utf-8") as seen_tracks,\
    open(NEW_TRACKS,"r", encoding="utf-8") as new_tracks:
        seen_artists = json.load(seen_artists)
        seen_tracks = json.load(seen_tracks)
        new_tracks = json.load(new_tracks)

    return seen_artists, seen_tracks, new_tracks


def search_artist(api_key, seen_artists, limit = 10):
    new_artist = []
    url = "https://ws.audioscrobbler.com/2.0/"

    res = requests.get(
        url,
        params={
            "method": "chart.gettopartists",
            "api_key": api_key,
            "format": "json",
            "limit": limit,
            "page": 1
        }
    )

    page = res.json()["artists"]["artist"]

    for artist in page:
        if normalize(artist["name"]) in seen_artists:
            continue
        new_artist.append(artist["name"])

    return new_artist




def search_tracks(api_key, new_artists, seen_tracks, limit = 10):
    new_artist_and_tracks = {}

    for artist in new_artists:
        artist_track = []
        url = "https://ws.audioscrobbler.com/2.0/"

        res = requests.get(
            url,
            params={
                "method": "artist.gettoptracks",
                "artist": artist,
                "api_key": api_key,
                "format": "json",
                "limit": limit,
                "autocorrect": 1
            }
        )

        if res.status_code != 200:
            print("Last.fm error:", artist, res.status_code, res.text)
            continue

        data = res.json()

        if "toptracks" not in data:
            print("No toptracks:", artist)
            continue

        tracks = data["toptracks"]["track"]

        for track in tracks:
            if normalize(str(artist + track["name"])) in seen_tracks:
                continue
            artist_track.append(track["name"])

        new_artist_and_tracks[artist]= artist_track

        time.sleep(0.5)

    return new_artist_and_tracks


def reload(new_artists_and_tracks, seen_artists, seen_tracks, new_tracks):
    for artist, tracks in new_artists_and_tracks.items():
        seen_artists[normalize(artist)] = True

        for track in tracks:
            seen_tracks[normalize(artist + track)] = True
            new_tracks.append(normalize(artist + track))

    

    with open(SEEN_ARTISTS, "w", encoding="utf-8") as f:
        json.dump(seen_artists, f, ensure_ascii=False, indent=4)

    with open(SEEN_TRACKS, "w", encoding="utf-8") as f:
        json.dump(seen_tracks, f, ensure_ascii=False, indent=4)

    with open(NEW_TRACKS, "w", encoding="utf-8") as f:
        json.dump(new_tracks, f, ensure_ascii=False, indent=4)


    
    
        

def collect():
    seen_artists, seen_tracks, new_tracks = load()

    new_artists = search_artist(API_KEY, seen_artists)
    new_artists_and_tracks = search_tracks(API_KEY, new_artists, seen_tracks)

    reload(new_artists_and_tracks, seen_artists, seen_tracks, new_tracks)


if __name__ == "__main__":
    collect()