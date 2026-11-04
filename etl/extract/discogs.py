import requests
import os

from dotenv import load_dotenv
from common.etlerror import Etlerror

##============================================================================
##============================================================================
load_dotenv()
DISCOGS_TOKEN = os.getenv("DISCOGS")
##============================================================================
##============================================================================


##discorg search=======================================================================
##============================================================================
def search(artist, track):
    genres = []

    try:
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
    except Exception as err:
        raise Etlerror(location="discogs", track = track, error= err)

    try:
        data = res.json()
    except Exception as err:
        print(data)
        raise Etlerror(location="discogs", track=track, error = err)

    # 검색 결과 없음
    if "results" not in data or not data["results"]:
         raise Etlerror(location="discogs", track = track, error="no data")


    release = data["results"][0]

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
##============================================================================
##============================================================================
