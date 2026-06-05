import requests
import os
from dotenv import load_dotenv

load_dotenv()

DISCOGS_TOKEN = os.getenv("DISCOGS")


def Discogs_API(artist, track):

    res = requests.get(
        "https://api.discogs.com/database/search",
        headers={
            "Authorization": f"Discogs token={DISCOGS_TOKEN}",
            "User-Agent": "MusicRecommendationProject/1.0"
        },
        params={
            "artist": artist,
            "track": track,
            "type": "release"
        }
    )

    print(f"discogs status : {res.status_code}")

    data = res.json()

    # 검색 결과 없음
    if "results" not in data or not data["results"]:
        return []

    release = data["results"][0]

    genres = []

    # genre
    if "genre" in release:
        genres.extend(release["genre"])

    # style
    if "style" in release:
        genres.extend(release["style"])

    # normalize + 중복 제거
    genres = list(set(
        genre.lower().replace("-", "").replace(" ", "")
        for genre in genres
    ))

    return genres
