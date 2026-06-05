from pathlib import Path
import json
import time

from Make_Raw_Data import Reccobeats_API as Reccobeats
from Make_Raw_Data import Lastfm_API as Lastfm
from Make_Raw_Data import Spotify_API as Spotify
from Make_Raw_Data import Discogs_API as Discogs


BASE_DIR = Path(__file__).parent

def make_metadata(query):
    metadatas = []

    # Spotify metadata 생성
    token = Spotify.get_access_token()

    
    Spotify.Spotify_API(query, metadatas, token)
    time.sleep(2)

    if(len(metadatas) == 1):
        reccobeats_metadatas = Reccobeats.Reccobeats_one(metadatas[0])
    else:
        reccobeats_metadatas = Reccobeats.Reccobeats(metadatas)["content"]

    combine_metadatas_reccobeats_metadatas(
        metadatas,
        reccobeats_metadatas
    )


    metadatas_idx = 0
    # Lastfm + Discogs 장르 추가
    for metadata in metadatas:

        # 빈 metadata skip
        if not metadata:
            metadatas_idx += 1
            continue

        fallback_genre = Discogs.Discogs(
                metadata["artist"],
                metadata["track"]
            )
        
        
        if fallback_genre:
            metadatas[metadatas_idx]["genre"] = fallback_genre
        else:
            genre = Lastfm.Lastfm_API(
                metadata["artist"],
                metadata["track"]
            )
            metadatas[metadatas_idx]["genre"] = genre

        time.sleep(1)
        metadatas_idx += 1
    return metadatas


def combine_metadatas_reccobeats_metadatas(
        metadatas,
        reccobeats_metadatas):

    # metadatas를 기준으로 병합
    metadatas_idx = 0
    reccobeats_metadatas_idx = 0

    while metadatas_idx < len(metadatas):

        # Spotify 검색 실패 metadata
        if not metadatas[metadatas_idx]:
            metadatas_idx += 1
            continue

        # Reccobeats 응답 범위 검사
        if reccobeats_metadatas_idx < len(reccobeats_metadatas):

            metadatas[metadatas_idx]["tempo"] = (
                reccobeats_metadatas[reccobeats_metadatas_idx]["tempo"]
            )

            metadatas[metadatas_idx]["key"] = (
                reccobeats_metadatas[reccobeats_metadatas_idx]["key"]
            )

            metadatas[metadatas_idx]["mode"] = (
                reccobeats_metadatas[reccobeats_metadatas_idx]["mode"]
            )

            reccobeats_metadatas_idx += 1
            metadatas_idx += 1

        else:
            return
        
def clean_data(metadatas):
    required_keys = ["spotify_id", "artist", "track", "tempo", "key", "mode", "genre"]

    return [
        metadata
        for metadata in metadatas
        if (metadata 
            and all(key in metadata for key in required_keys)
            and metadata["genre"])
    ]


def main(query):
    metadatas = make_metadata(query)
    if(len(metadatas) == 1):
        clean_metadata = clean_data(metadatas)
    else:
        clean_metadata = clean_data(metadatas[0])
    # clean_metadata = clean_data(metadatas[0])

    with open("Data/Raw_metadata.json", "r", encoding="utf-8") as file:
        old_data = json.load(file)

    old_data.extend(clean_metadata)

    with open("Data/Raw_metadata.json", "w", encoding="utf-8") as file:
        json.dump(
            old_data,
            file,
            ensure_ascii=False,
            indent=4
        )

    return clean_metadata


if __name__ == "__main__":
    with open(BASE_DIR / "dataset.json", "r", encoding="utf-8") as file:
        dataset = json.load(file)
