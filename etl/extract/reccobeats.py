import requests
from common.etlerror import Etlerror

##============================================================================
##============================================================================
RECCOBEATS_COUNT_LIMIT = 30
##============================================================================
##============================================================================



## reccobeats search========================================================================
##============================================================================
def search(spotify_raw_data):

    raw_data_len = 0
    reccobeats_raw_data = {}

    # reccobeats는 배열로 다수의 곡을 요청하는 것이 가능
    while raw_data_len < len(spotify_raw_data):
        return_data = {}
        quries = spotify_raw_data[raw_data_len : raw_data_len + RECCOBEATS_COUNT_LIMIT]

        raw_data_len = min(raw_data_len + RECCOBEATS_COUNT_LIMIT, len(spotify_raw_data))

        try:
            res = requests.get(
                "https://api.reccobeats.com/v1/audio-features",
                params=[("ids", query["spotify_id"]) for query in quries if query],
                timeout=20,
            )

            return_data = res.json()

        except Exception as err:
            raise Etlerror(location="reccobeats", track = quries, error=err)

        if "content" in return_data:
            for track in return_data["content"]:
                reccobeats_raw_data[track["href"].split("/track/")[1]] = track
        else:
            raise Etlerror(location="reccobeats", track=quries, error="no data")

    return reccobeats_raw_data


##============================================================================
##============================================================================
