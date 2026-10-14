import requests
##============================================================================
##============================================================================
RECCOBEATS_COUNT_LIMIT = 30
##============================================================================
##============================================================================


## reccobeats search========================================================================
##============================================================================
def search(raw_data):

    raw_data_len = 0
    return_value = []

    #reccobeats는 배열로 다수의 곡을 요청하는 것이 가능
    while(raw_data_len < len(raw_data)):
        quries = raw_data[
            raw_data_len:raw_data_len + RECCOBEATS_COUNT_LIMIT
        ]

        raw_data_len = min(
            raw_data_len + RECCOBEATS_COUNT_LIMIT,
            len(raw_data)
        )

        res = requests.get(
            "https://api.reccobeats.com/v1/audio-features",
            params=[("ids", query["spotify_id"]) for query in quries if query]
        )

        batch_return_value = res.json()

        if "content" in batch_return_value:
            return_value.extend(batch_return_value["content"])
        else:
            #content가 없는 경우의 리턴처리: 추후 작성 에정
            pass

    return return_value
##============================================================================
##============================================================================
