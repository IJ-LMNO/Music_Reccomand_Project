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
COLLECTED_TRACKS = BASE_DIR / "data" / "extract" / "collected_track_title.json"
NEW_TRACKS = BASE_DIR / "data" / "extract" / "new_tracks.json"
COUNTRY_PAGE = BASE_DIR / "data" / "extract" / "country_page.json"


def load():
    with open(SEEN_ARTISTS, "r", encoding="utf-8") as seen_artists,\
    open(COLLECTED_TRACKS, "r", encoding="utf-8") as collected_tracks,\
    open(NEW_TRACKS,"r", encoding="utf-8") as new_tracks,\
    open(COUNTRY_PAGE, "r", encoding="utf-8") as country_page:
        seen_artists = json.load(seen_artists)
        collected_tracks = json.load(collected_tracks)
        new_tracks = json.load(new_tracks)
        country_page = json.load(country_page)

    return seen_artists, collected_tracks, new_tracks, country_page


def decied_page(country_page):
    country = min(country_page, key = country_page.get)
    page = country_page[country]

    return country, page


def search_artist(api_key, seen_artists, country_page, limit = 10):
    new_artist = []
    url = "https://ws.audioscrobbler.com/2.0/"

    country, page = decied_page(country_page)
    res = requests.get(
        url,
        params={
            "method": "geo.gettopartists",
            "country" : country,
            "api_key": api_key,
            "format": "json",
            "limit": limit,
            "page": page
        }
    )

    artists = res.json()["topartists"]["artist"]

    for artist in artists:
        if normalize(artist["name"]) in seen_artists:
            continue
        new_artist.append(artist["name"])

    return new_artist




def search_tracks(api_key, new_artists, collected_tracks, limit = 10):
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
            raise RuntimeError(
                f"Last.fm error: {artist}, {res.status_code}"
            )

        data = res.json()

        if "toptracks" not in data:
            print("No toptracks:", artist)
            continue

        tracks = data["toptracks"]["track"]

        for track in tracks:
            if normalize(str(artist + track["name"])) in collected_tracks:
                continue
            artist_track.append(track["name"])

        new_artist_and_tracks[artist]= artist_track

        time.sleep(0.5)

    return new_artist_and_tracks


def reload(new_artists_and_tracks, seen_artists, collected_tracks, new_tracks, country_page):
    for artist, tracks in new_artists_and_tracks.items():
        seen_artists[normalize(artist)] = True

        for track in tracks:
            key = normalize(artist + track)

            if key not in collected_tracks and key not in new_tracks:
                new_tracks.append(key)

    country, _ = decied_page(country_page)
    country_page[country] += 1
    

    with open(SEEN_ARTISTS, "w", encoding="utf-8") as f:
        json.dump(seen_artists, f, ensure_ascii=False, indent=4)

    with open(NEW_TRACKS, "w", encoding="utf-8") as f:
        json.dump(new_tracks, f, ensure_ascii=False, indent=4)

    with open(COUNTRY_PAGE, "w", encoding="utf-8") as f:
        json.dump(country_page, f, ensure_ascii=False, indent=4)


    
    
        

def collect():
    seen_artists, collected_tracks, new_tracks, country_page = load()

    new_artists = search_artist(API_KEY, seen_artists, country_page)
    new_artists_and_tracks = search_tracks(API_KEY, new_artists, collected_tracks)

    reload(new_artists_and_tracks, seen_artists, collected_tracks, new_tracks, country_page)


if __name__ == "__main__":
    collect()