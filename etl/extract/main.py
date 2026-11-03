import json
import time
import requests
from pathlib import Path

from extract import reccobeats, lastfm, spotify, discogs
from common.normalize import normalize
from common.etlerror import Etlerror


# =========================================================
# 환경 설정 및 데이터 경로
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "extract"

SPOTIFY_ACCESS_TIME_LIMIT = 5

DATA_FILES = {
    "new_tracks": DATA_DIR / "new_tracks.json",
    "collected_spotify_id": DATA_DIR / "collected_spotify_id.json",
    "collected_track_title": DATA_DIR / "collected_track_title.json",
    "collected_track_and_spotify_id": DATA_DIR / "collected_track_and_spotify_id.json",
    "raw_data": DATA_DIR / "raw_data.json",
    "failed_data": DATA_DIR / "failed_tracks.json",
}


# =========================================================
# JSON 파일 로드 및 저장
# =========================================================


def load():
    data = {}

    for name, path in DATA_FILES.items():
        with path.open("r", encoding="utf-8") as f:
            data[name] = json.load(f)

    return data


def reload(data):
    for name, path in DATA_FILES.items():
        with path.open("w", encoding="utf-8") as f:
            json.dump(data[name], f, ensure_ascii=False, indent=4)


# =========================================================
# Spotify / ReccoBeats 데이터 병합
# =========================================================


def combine(fail_track, spotify_raw_data, reccobeats_raw_data):
    combine_raw_data = []

    for track in spotify_raw_data:
        if not track:
            continue

        if track["spotify_id"] in reccobeats_raw_data:
            track.update(reccobeats_raw_data[track["spotify_id"]])
            combine_raw_data.append(track)

        else:
            fail_track.append(
                {"location": "reccobeats", "track": track["track"], "error": "no data"}
            )

    return combine_raw_data, fail_track

# =========================================================
# api
# =========================================================


def spotify_api(query, token):
    try:
        spotify_result = spotify.search(query, token)
    except Exception:
        raise

    return spotify_result


def reccobeats_api(spotify_raw_data):
    try:
        reccobeats_raw_data = reccobeats.search(spotify_raw_data)
    except Exception:
        raise

    return reccobeats_raw_data


def discogs_api(track):
    try:
        discogs_raw_data = discogs.search(track["artist"], track["track"])
    except:
        raise

    return discogs_raw_data


def lastfm_api(track):
    try:
        lastfm_raw_data = lastfm.search(track["artist"], track["track"])
    except:
        raise

    return lastfm_raw_data


# =========================================================
# 필수 메타데이터 검증
# =========================================================


# def clean_raw_data(metadatas):
#     required_keys = ["spotify_id", "artist", "track", "tempo", "key", "mode", "genre"]

#     cleaned = []

#     for metadata in metadatas:
#         if not metadata:
#             continue

#         if not all(key in metadata for key in required_keys):
#             continue

#         if not metadata["spotify_id"]:
#             continue

#         if not metadata["artist"]:
#             continue

#         if not metadata["track"]:
#             continue

#         if metadata["tempo"] is None:
#             continue

#         if metadata["key"] is None or metadata["key"] == "":
#             continue

#         if metadata["mode"] is None:
#             continue

#         if not metadata["genre"]:
#             continue

#         cleaned.append(metadata)

#     return cleaned


# =========================================================
# Spotify ID 기준으로 중복 데이터 제거
# =========================================================


def eliminate_duplicate(data, raw_data):

    eliminate_duplicate_raw_data = []
    for track in raw_data:
        spotify_id = track["spotify_id"]

        if spotify_id in data["collected_spotify_id"]:
            continue

        eliminate_duplicate_raw_data.append(track)
        data["collected_spotify_id"][spotify_id] = True

        # 가수 + 곡명 기준 검색용 매핑 갱신
        normalized_title = normalize(track["artist"] + track["track"])

        data["collected_track_title"][normalized_title] = True

        data["collected_track_and_spotify_id"][normalized_title] = spotify_id

    return eliminate_duplicate_raw_data


# =========================================================
# Extract 메인 로직
# =========================================================
def extract():
    # 기존 JSON 데이터 불러오기
    data = load()
    queries = data["new_tracks"]

    if not queries:
        print("검색할 노래가 없음")
        return

    # 음악 메타데이터 수집 및 검증
    raw_data = []
    fail_track = []
    while True:
        if not queries:
            break

        batch = queries[0:10]


        # spotify관련 api 및 전처리
        spotify_raw_data = []
        for track in batch:
            token = spotify.get_access_token()

            try:
                spotify_result = spotify_api(track, token)
            except Etlerror as err:
                print("예외 발생 : track 보존")
                fail_track.append(
                    {
                        "location": err.location,
                        "track": err.track,
                        "error": err.error,
                    }
                )
                continue

            # spotify에서 반환된 유사곡들 중 가장 유사도가 높은 곡 하나 특정
            spotify_track = spotify.match(track, spotify_result)

            # 특정된 곡을 spotify_raw_data에 넣어 보관
            spotify.append(spotify_track, spotify_raw_data)



        # reccobeats관련 api 및 전처리
        try:
            reccobeats_raw_data = reccobeats_api(spotify_raw_data)
        except Etlerror as err:

            location = err.location
            error = err.error

            for track in err.track:
                fail_track.append(
                    {
                        "location": location,
                        "track": track,
                        "error": error,
                    }
            )
            
            del queries[0:10]
            continue

        # spotify_raw_data와 reccobeats_raw_data를 combine
        combine_raw_data, fail_track = combine(
            fail_track, spotify_raw_data, reccobeats_raw_data
        )




        # 장르 수집을 위한 discogs, lastfm api및 전처리
        for track in combine_raw_data:
            if not track:
                continue

            try:
                discogs_raw_data = discogs_api(track)
            except Etlerror as err:
                print("예외 발생 : track 보존")
                fail_track.append(
                    {
                        "location": err.location,
                        "track": err.track,
                        "error": err.error,
                    }
                )

            if not discogs_raw_data:
                try:
                    lastfm_raw_data = lastfm_api(track)
                except Etlerror as err:
                    print("예외 발생 : track 보존")
                    fail_track.append(
                        {
                            "location": err.location,
                            "track": err.track,
                            "error": err.error,
                        }
                    )

            if discogs_raw_data:
                track["genre"] = discogs_raw_data
            else:
                if lastfm_raw_data:
                    track["genre"] = lastfm_raw_data
                else:
                    track["genre"] = []

        del queries[0:10]
        raw_data.extend(combine_raw_data)

        time.sleep(SPOTIFY_ACCESS_TIME_LIMIT)

    # Spotify ID 기준으로 중복 데이터 제거
    eliminate_duplicate_raw_data = eliminate_duplicate(data, raw_data)

    # 기존 Raw Data에 신규 데이터 추가
    data["raw_data"].extend(eliminate_duplicate_raw_data)

    # 검색에 실패한 데이터 저장
    data["failed_data"].extend(fail_track)

    # 변경된 JSON 데이터 저장
    reload(data)

    return True
