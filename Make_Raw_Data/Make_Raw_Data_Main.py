from pathlib import Path
import json
import time

import Reccobeats_API as Reccobeats
import Lastfm_API as Lastfm
import Spotify_API as Spotify
import Discogs_API as Discogs

BASE_DIR = Path(__file__).parent

def normalize(text):
    return (
        text.lower()
        .replace(" ", "")
        .replace("-", "")
        .replace("!", "")
        .replace("'", "")
        .replace("(", "")
        .replace(")", "")
    )

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

            recco_data = reccobeats_metadatas[reccobeats_metadatas_idx]

            metadatas[metadatas_idx]["tempo"] = recco_data["tempo"]
            metadatas[metadatas_idx]["key"] = recco_data["key"]
            metadatas[metadatas_idx]["mode"] = recco_data["mode"]

            metadatas[metadatas_idx]["energy"] = recco_data.get("energy", 0.5)
            metadatas[metadatas_idx]["danceability"] = recco_data.get("danceability", 0.5)
            metadatas[metadatas_idx]["valence"] = recco_data.get("valence", 0.5)
            metadatas[metadatas_idx]["acousticness"] = recco_data.get("acousticness", 0.5)

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
    size = 10

    with open("Make_Raw_Data/Dataset.json", "r", encoding="utf-8") as dataset:
        dataset = json.load(dataset)

    with open("Make_Raw_Data/Raw_track_name_index.json", "r", encoding="utf-8") as raw_track_name_index:
        raw_track_name_index = json.load(raw_track_name_index)

    with open("Data/Raw_metadata.json", "r", encoding="utf-8") as file:
        new_data = json.load(file)

    eliminate_overlap_query = []
    for track in dataset:
        if(len(eliminate_overlap_query) > size):
            metadatas = make_metadata(eliminate_overlap_query)
            clean_metadatas = clean_metadata(metadatas)

            new_data.extend(clean_metadatas)
            
            with open("Data/Raw_metadata.json", "w", encoding="utf-8") as file:
                json.dump(
                    new_data,
                    file,
                    ensure_ascii=False,
                    indent=4
                )

            for clean_track in clean_metadatas:
                key = normalize(clean_track["artist"] + clean_track["track"])
                
                if key not in raw_track_name_index:
                    raw_track_name_index[key] = True
                else:
                    continue


            with open("Make_Raw_Data/Raw_track_name_index.json", "w", encoding="utf-8") as file:
                json.dump(raw_track_name_index, file, ensure_ascii=False, indent=4)

            print(f"{len(new_data)}곡 저장 완료")
            time.sleep(20)

            eliminate_overlap_query = []
        else:
            if normalize(track) not in raw_track_name_index:
                eliminate_overlap_query.append(track)
            else:
                continue
    

    if eliminate_overlap_query:
            metadatas = make_metadata(eliminate_overlap_query)
            clean_metadatas = clean_metadata(metadatas)

            new_data.extend(clean_metadatas)
            eliminate_overlap_query = []


    with open("Data/Raw_metadata.json", "w", encoding="utf-8") as file:
        json.dump(
            new_data,
            file,
            ensure_ascii=False,
            indent=4
        )
    for track in clean_metadatas:
        key = normalize(normalize(track["artist"] + track["track"]))
        
        if key not in raw_track_name_index:
            raw_track_name_index[key] = True
        else:
            continue


    with open("Make_Raw_Data/Raw_track_name_index.json", "w", encoding="utf-8") as file:
        json.dump(raw_track_name_index, file, ensure_ascii=False, indent=4)
    
    print(f"마지막 배치 저장 완료")


    print("raw_metadata.json 저장 완료\n")


if __name__ == "__main__":
    main()