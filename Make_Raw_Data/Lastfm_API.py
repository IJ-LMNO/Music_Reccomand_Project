import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("LASTFM")

def Lastfm_API(artist, track, limit=10):
    res = requests.get(
        "https://ws.audioscrobbler.com/2.0/",
        params={
            "method": "track.getTopTags",
            "artist" : artist,
            "track": track,
            "api_key": API_KEY,
            "format": "json",
            "autocorrect": 1,
            "limit": limit
        }
    )

    tags = res.json()["toptags"]["tag"]

    
    returnarr = []
    for obj in tags:
        toggle = True
        if(obj["count"] > 10):
            normalizeobj = obj["name"].lower().replace("-","").replace(" ","")
            for genre in returnarr:
                if(genre == normalizeobj):
                   toggle = False 
            if(toggle == True):
                returnarr.append(normalizeobj)
                    

    return returnarr