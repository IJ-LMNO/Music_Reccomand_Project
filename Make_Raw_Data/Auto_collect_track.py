import json
import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("LASTFM")

ARTISTS = [
  "BLACKPINK",
  "NewJeans",
  "ILLIT",
  "IVE",
  "ITZY",
  "(G)I-DLE",
  "STAYC",
  "aespa",
  "LE SSERAFIM",
  "TWICE",
  "Red Velvet",
  "NMIXX",
  "BABYMONSTER",
#   "KISS OF LIFE",
#   "fromis_9",
#   "OH MY GIRL",
#   "GFRIEND",
#   "MAMAMOO",
#   "ENHYPEN",
#   "Stray Kids",
#   "SEVENTEEN",
#   "BTS",
#   "TXT",
#   "RIIZE",
#   "NCT DREAM",
#   "YOASOBI",
#   "Ado",
#   "Official HIGE DANdism",
#   "Kenshi Yonezu",
#   "Vaundy",
#   "King Gnu",
#   "Mrs. GREEN APPLE",
#   "LiSA",
#   "Aimyon",
#   "Eve",
#   "back number",
#   "Taylor Swift",
#   "The Weeknd",
#   "Dua Lipa",
#   "Ariana Grande",
#   "Olivia Rodrigo",
#   "Billie Eilish",
#   "Sabrina Carpenter",
#   "Doja Cat",
#   "SZA",
#   "Post Malone",
#   "Ed Sheeran",
#   "Bruno Mars",
#   "Justin Bieber",
#   "Lady Gaga"
]



def get_artist_top_tracks(api_key, artist_name, limit=10):
    url = "https://ws.audioscrobbler.com/2.0/"

    res = requests.get(
        url,
        params={
            "method": "artist.gettoptracks",
            "artist": artist_name,
            "api_key": api_key,
            "format": "json",
            "limit": limit,
            "autocorrect": 1
        }
    )

    if res.status_code != 200:
        print("Last.fm error:", artist_name, res.status_code, res.text)
        return []

    data = res.json()

    if "toptracks" not in data:
        print("No toptracks:", artist_name, data)
        return []

    tracks = data["toptracks"].get("track", [])

    result = []

    for track in tracks:
        track_name = track["name"]
        result.append(f"{artist_name} {track_name}")

    return result


def make_dataset(api_key, artists, output_path="Make_Raw_Data/dataset.json"):
    dataset = []
    seen = set()

    for artist in artists:
        tracks = get_artist_top_tracks(api_key, artist, limit=10)

        for query in tracks:
            key = query.lower().replace(" ", "")

            if key in seen:
                continue

            seen.add(key)
            dataset.append(query)

        print(artist, "->", len(tracks))
        time.sleep(0.3)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(dataset, file, ensure_ascii=False, indent=4)

    print("saved:", output_path)
    print("track count:", len(dataset))


if __name__ == "__main__":
    make_dataset(LASTFM_API_KEY, ARTISTS)