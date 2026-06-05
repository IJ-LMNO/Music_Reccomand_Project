import requests

def Reccobeats_one(metadata):
    spotify_id = metadata["spotify_id"]

    res = requests.get(
        "https://api.reccobeats.com/v1/audio-features",
        params={
            "ids": spotify_id
        }
    )

    res.raise_for_status()

    data = res.json()
    return data['content']   

def Reccobeats(metadatas):

    all_contents = []

    for i in range(0, len(metadatas), 20):

        batch = metadatas[i:i+20]

        res = requests.get(
            "https://api.reccobeats.com/v1/audio-features",
            params=[("ids", metadata["spotify_id"]) for metadata in batch if metadata]
        )

        print(
            f"reccobeats api status ({i} ~ {i + len(batch) - 1}) : "
            + str(res.status_code)
        )

        result = res.json()

        if "content" in result:
            all_contents.extend(result["content"])

    return {
        "content": all_contents
    }