import json
import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("LASTFM")

ARTISTS = [

  "Coldplay",
  "Imagine Dragons",
  "Maroon 5",
  "OneRepublic",
  "Linkin Park",
  "Green Day",
  "Fall Out Boy",
  "Panic! At The Disco",
  "Paramore",
  "The Chainsmokers",
  "Alan Walker",
  "Avicii",
  "Martin Garrix",
  "Calvin Harris",
  "Zedd",
  "David Guetta",
  "Kygo",
  "Clean Bandit",
  "Sam Smith",
  "Shawn Mendes",

  "Charlie Puth",
  "Lewis Capaldi",
  "James Arthur",
  "Harry Styles",
  "Niall Horan",
  "Lauv",
  "Conan Gray",
  "Troye Sivan",
  "Benson Boone",
  "Tate McRae",

  "Selena Gomez",
  "Camila Cabello",
  "Halsey",
  "Miley Cyrus",
  "Katy Perry",
  "Rihanna",
  "Lorde",
  "Anne-Marie",
  "Meghan Trainor",
  "Zara Larsson",

  "Drake",
  "Kendrick Lamar",
  "J. Cole",
  "Travis Scott",
  "Future",
  "21 Savage",
  "Lil Baby",
  "Metro Boomin",
  "Tyler, The Creator",
  "Jack Harlow",

  "AKMU",
  "IU",
  "BOL4",
  "Heize",
  "Taeyeon",
  "Paul Kim",
  "MeloMance",
  "Zion.T",
  "Crush",
  "DEAN",

  "XG",
  "tripleS",
  "QWER",
  "BOYNEXTDOOR",
  "TWS",
  "ZEROBASEONE",
  "TREASURE",
  "ATEEZ",
  "MONSTA X",
  "THE BOYZ"

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
    make_dataset(API_KEY, ARTISTS)