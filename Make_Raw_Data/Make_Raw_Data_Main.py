from pathlib import Path
import json
import time

import Reccobeats_API as Reccobeats
import Lastfm_API as Lastfm
import Spotify_API as Spotify
import Discogs_API as Discogs

BASE_DIR = Path(__file__).parent

def make_metadata(sample_queries):
    metadatas = []

    # Spotify metadata 생성
    token = Spotify.get_access_token()

    for query in sample_queries:
        Spotify.Spotify_API(query, metadatas, token)
        time.sleep(2)

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

        fallback_genre = Discogs.Discogs_API(
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
        
def clean_metadata(metadatas):
    required_keys = ["spotify_id", "artist", "track", "tempo", "key", "mode", "genre"]

    return [
        metadata
        for metadata in metadatas
        if (metadata 
            and all(key in metadata for key in required_keys)
            and metadata["genre"])
    ]


def main():
    size = 100
    new_data = []

    with open("Make_Raw_Data/dataset.json", "r", encoding="utf-8") as dataset:
        dataset = json.load(dataset)
    dataset_len = len(dataset)

    for start in range(0, dataset_len, size):
        sample_queries = dataset[start:start + size]

        metadatas = make_metadata(sample_queries)
        clean_metadatas = clean_metadata(metadatas)

        new_data.extend(clean_metadatas)

        time.sleep(10)

    with open("Data/Raw_metadata.json", "w", encoding="utf-8") as file:
        json.dump(
            new_data,
            file,
            ensure_ascii=False,
            indent=4
        )

    print("raw_metadata.json 저장 완료\n")


if __name__ == "__main__":
    main()