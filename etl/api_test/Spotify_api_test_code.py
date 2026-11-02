import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


def get_access_token():
    auth = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_b64 = base64.b64encode(auth.encode()).decode()

    res = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={"grant_type": "client_credentials"}
    )

    res.raise_for_status()
    return res.json()["access_token"]

def spotify():
    token = get_access_token()

    res = requests.get(
    "https://api.spotify.com/v1/search",
    headers={"Authorization": f"Bearer {token}"},
        params={
            "q": "BLACKPINK Pink Venom",
            "type": "track",
            "limit": 5        
        }
    )

    print(res.json()["tracks"]["items"][0])

def Spotify_Artist_Genre():

    token = get_access_token()

    res = requests.get(
        f"https://api.spotify.com/v1/artists/{"41MozSoPIsD1dJM0CLPjZF"}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    print(f"spotify status : {res.status_code}")

    data = res.json()
    print(data)

    # genres key 존재 여부 검사
    if "genres" not in data:
        return []

    return data["genres"]


if __name__ == "__main__":
    Spotify_Artist_Genre()