import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("LASTFM")

def Lastfm():
    res = requests.get(
        "https://ws.audioscrobbler.com/2.0/",
        params={
            "method": "track.getTopTags",
            "artist" : "blackpink",
            "track": "DDU-DU DDU-DU",
            "api_key": API_KEY,
            "format": "json",
            "autocorrect": 1,
            "limit": 10
        }
    )

    tags = res.json()

    print(tags)


if __name__ == "__main__":
    Lastfm()