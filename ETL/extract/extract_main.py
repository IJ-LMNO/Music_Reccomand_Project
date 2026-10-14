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

    # spotify는 개별 요청 검색만을 지원
    for query in quries:
        spotify_return_query = spotify.search(query, token)
        data = spotify.match(query, spotify_return_query)
        spotify.append(data, spotify_raw_data)

        #@@spotify api 접근 제한 확인해야 함
        time.sleep(SPOTIFY_ACCESS_TIME_LIMIT)

    ##============================================================================
    ##============================================================================



    ##reccobeats=======================================================================
    ##============================================================================

    # reccobeats는 개별 검색, 다수 검색 모두 지원
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

        # discogs는 개별 검색 요청만을 지원
        genre = discogs.search( data["artist"], data["track"])

        # discogs에 장르가 없는 경우 lastfm을 통한 장르 추가
        if genre:
            spotify_raw_data[data_idx]["genre"] = genre
        else:
            # lastfm는 개별 검색 요청만을 지원
            genre = lastfm.search( data["artist"], data["track"] )
            spotify_raw_data[data_idx]["genre"] = genre


        # discogs는 분당에 60번 호출 제한이 있음
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
        artist_top_tracks = json.load(artist_top_tracks)

    # artist_top_track에 저장된 노래에 대한 raw_Data 생성
    ## artist_top_track에 데이터가 없는 경우 노래가 없음을 알린 후 return
    if(len(artist_top_tracks) == 0):
        print("검색할 노래가 없음")
        return
    else:
        raw_data = clean_raw_data(make_raw_data(artist_top_tracks))

    with open("data/collected_spotify_id", "r", encoding="utf-8") as collected_spotify_id:
        collected_spotify_id = json.load(collected_spotify_id)


    # collected_spotify_id와의 중복 검사 후 중복 제거된 곡들을 elminate_duplicated_raw_dat에 저장
    eliminate_duplicated_raw_data = []
    for data in raw_data:
        spotify_id = data["spotify_id"]

        if spotify_id in collected_spotify_id:
            continue

        eliminate_duplicated_raw_data.append(data)
        collected_spotify_id[spotify_id] = True


    # collected_track_title과 collected_track_title_and_spotify_id에 저장할 dict 생성
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
        open("data/collected_track_title_and_spotify_id", "r", encoding="utf-8") as collected_track_title_and_spotify_id
    ):
        saved_track_title = json.load(collected_track_title)
        saved_track_title_and_spotify_id = json.load(collected_track_title_and_spotify_id)
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

    ##@@이번 main실행에 따른 artist_top_track 내용을 삭제할지 아니면 가지고 있을지에 대한 규칙 생각
    ## 1. 전체 삭제
    ## 2. 탐색되지 않은 노래만 삭제
    ## 3. 전체를 보존

    return True

##============================================================================
##============================================================================

