import requests
API_KEY = None

def Lastfm():
    res = requests.get(
        "https://ws.audioscrobbler.com/2.0/",
        params={
            "method": "track.getTopTags",
            "artist" : "qwer",
            "track": "고백중독",
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