import requests
import os
from dotenv import load_dotenv
from common.etlerror import Etlerror


##============================================================================
##====================================================================W========
load_dotenv()
API_KEY = os.getenv("LASTFM")
##============================================================================
##============================================================================


## lastfm genre search=========================================================================
##============================================================================
def search(artist, track, limit=10):
    try:
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
    except Exception as err:
        raise Etlerror(location="lastfm", track = track, error=err)

    try:
        tags = res.json()["toptags"]["tag"]
    except Exception as err:
        raise Etlerror(location="lastfm", track = track, error=err)

    if not tags:
        raise Etlerror(location="lastfm", track = track, error="no data")


    
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
##============================================================================
##============================================================================
