from pathlib import Path
import json
import time

import Music_Reccomand_Project.ETL.Extract.reccobeats as reccobeats
import Music_Reccomand_Project.ETL.Extract.lastfm as lastfm
import Music_Reccomand_Project.ETL.Extract.spotify as spotify
import Music_Reccomand_Project.ETL.Extract.discogs as discogs
from Music_Reccomand_Project.ETL.Extract.common.normalize import normalize 


##============================================================================
##============================================================================

BASE_DIR = Path(__file__).parent
SPOTIFY_ACCESS_TIME_LIMIT = 1

##============================================================================
##============================================================================




## spotify & recoobeats raw data 합병 =========================================================================
## =======================================================================
def combine(spotify_raw_data, reccobeats_raw_data):

    # metadatas를 기준으로 병합
    spotify_raw_data_idx = 0
    reccobeats_raw_data_idx = 0

    while spotify_raw_data_idx < len(spotify_raw_data):

        # Spotify_raw_data에서 검색 결과 곡이 없는 경우 : []
        # 따라서 []이 false로 처리되는 파이썬의 특징을 이용해 다음 index로 넘어감
        if not spotify_raw_data[spotify_raw_data_idx]:
            spotify_raw_data_idx += 1
            continue

        # Spotify_raw_data에서 []인 경우 조건문을 통해 reccobeats에서는 검색하지 않음
        # -> (params=[("ids", query["spotify_id"]) for query in quries if query])
        # spotify_raw_data_idx = []인 경우에 해당하는 query는 reccobeats_raw_data에 존재하지 않음
        if reccobeats_raw_data_idx < len(reccobeats_raw_data_idx):

            recco_data = reccobeats_raw_data[reccobeats_raw_data_idx]

            spotify_raw_data[spotify_raw_data_idx]["tempo"] = recco_data["tempo"]
            spotify_raw_data[spotify_raw_data_idx]["key"] = recco_data["key"]
            spotify_raw_data[spotify_raw_data_idx]["mode"] = recco_data["mode"]

            spotify_raw_data[spotify_raw_data_idx]["energy"] = recco_data.get("energy", 0.5)
            spotify_raw_data[spotify_raw_data_idx]["danceability"] = recco_data.get("danceability", 0.5)
            spotify_raw_data[spotify_raw_data_idx]["valence"] = recco_data.get("valence", 0.5)
            spotify_raw_data[spotify_raw_data_idx]["acousticness"] = recco_data.get("acousticness", 0.5)

            spotify_raw_data_idx += 1
            reccobeats_raw_data_idx += 1

        else:
            return
##============================================================================
##============================================================================



## raw data 생성========================================================================
##============================================================================
def make_raw_data(quries):
    spotify_raw_data = []
    token = spotify.get_access_token()

    ##spotify======================================================================
    ##============================================================================

    for query in quries:
        spotify_return_query = spotify.search(query, token)
        data = spotify.match(query, spotify_return_query)
        spotify.append(data, spotify_raw_data)

        ##spotify api 접근 제한 확인해야 함
        time.sleep(SPOTIFY_ACCESS_TIME_LIMIT)

    ##============================================================================
    ##============================================================================



    ##reccobeats=======================================================================
    ##============================================================================

    reccobeats_raw_data = reccobeats.search(spotify_raw_data)["content"]

    ##============================================================================
    ##============================================================================


    ##combine spotify & reccobeats raw data=======================================================================
    ##============================================================================

    combine(spotify_raw_data, reccobeats_raw_data)

    ##============================================================================
    ##============================================================================


    ##discogs + lastfm을 이용한 장르 추가=======================================================================
    ##============================================================================
    data_idx = 0

    # discogs 장르를 이용한 장르 추가
    for data in spotify_raw_data:

        # 빈 metadata skip
        if not data:
            data_idx += 1
            continue

        genre = discogs.search(
                data["artist"],
                data["track"]
            )

        # discogs에 장르가 없는 경우 lastfm을 통한 장르 추가
        if genre:
            spotify_raw_data[data_idx]["genre"] = genre
        else:
            genre = lastfm.search(
                data["artist"],
                data["track"]
            )
            spotify_raw_data[data_idx]["genre"] = genre


        time.sleep(1)

        data_idx += 1
    ##============================================================================
    ##============================================================================

    return spotify_raw_data
##============================================================================
##============================================================================


##============================================================================
##============================================================================       
def clean_raw_data(metadatas):
    required_keys = ["spotify_id", "artist", "track", "tempo", "key", "mode", "genre"]

    cleaned = []

    for metadata in metadatas:
        if not metadata:
            continue

        if not all(key in metadata for key in required_keys):
            continue

        if not metadata["spotify_id"]:
            continue

        if not metadata["artist"]:
            continue

        if not metadata["track"]:
            continue

        if metadata["tempo"] is None:
            continue

        if not metadata["key"]:
            continue

        if metadata["mode"] is None:
            continue

        if not metadata["genre"]:
            continue

        cleaned.append(metadata)

    return cleaned
##============================================================================
##============================================================================



##============================================================================
##============================================================================
def main():
    with open("data/artist_top_tracks.json", "r", encoding="utf-8") as artist_top_tracks:
        ## artist_top_tracks는  ["title1", "title2"]구조
        ## list로 반환
        artist_top_tracks = json.load(artist_top_tracks)


    raw_data = clean_raw_data(make_raw_data(artist_top_tracks))

    with open("data/collected_spotify_id", "r", encoding="utf-8") as collected_spotify_id:
        collected_spotify_id = json.load(collected_spotify_id)


    eliminate_duplicated_raw_data = []
    for data in raw_data:
        spotify_id = data["spotify_id"]

        if spotify_id in collected_spotify_id:
            continue

        eliminate_duplicated_raw_data.append(data)
        collected_spotify_id[spotify_id] = True


    track_title = {}
    track_title_and_spotify_id = {}
    for data in eliminate_duplicated_raw_data:
        track_title = normalize(data["artist"] + data["track"])
        track_title[track_title] = True
        track_title_and_spotify_id[track_title] = data["spotify_id"]

    # 기존 데이터 불러오기
    with (
        open("data/collected_track_title", "r", encoding="utf-8") as collected_track_title,
        open("data/raw_data", "r", encoding="utf-8") as raw_data,
        open("data/dataset_track_title_and_spotify_id", "r", encoding="utf-8") as dataset_track_title_and_spotify_id
    ):
        saved_track_title = json.load(collected_track_title)
        saved_track_title_and_spotify_id = json.load(dataset_track_title_and_spotify_id)
        saved_raw_data = json.load(raw_data)


    # 기존 데이터와 새로운 데이터 병합
    saved_track_title.update(track_title)
    saved_track_title_and_spotify_id.upadate(track_title_and_spotify_id)
    saved_raw_data.extend(eliminate_duplicated_raw_data)


    # 병합된 데이터 저장
    with (
        open("data/collected_spotify_id", "w", encoding="utf-8") as f1,
        open("data/collected_track_title", "w", encoding="utf-8") as f2,
        open("data/raw_data", "w", encoding="utf-8") as f3,
        open("data/dataset_track_title_and_spotify_id", "w", encoding="utf-8") as f4
    ):
        json.dump(
            collected_spotify_id,
            f1,
            ensure_ascii=False,
            indent=4
        )

        json.dump(
            saved_track_title,
            f2,
            ensure_ascii=False,
            indent=4
        )

        json.dump(
            saved_raw_data,
            f3,
            ensure_ascii=False,
            indent=4
        )

        json.dump(
            saved_track_title_and_spotify_id,
            f4,
            ensure_ascii=False,
            indent=4
        )

##============================================================================
##============================================================================


    

if __name__ == "__main__":
    main()