
import json
import time
import requests
from pathlib import Path

from extract import reccobeats, lastfm, spotify, discogs
from common.normalize import normalize

class Etlerror(Exception):
    def __init__(self, error_location, track, error):
        self.error_location = error_location
        self.track = track
        self.error = error

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
    "failed_data" : DATA_DIR / "failed_tracks.json"
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
            json.dump(
                data[name],
                f,
                ensure_ascii=False,
                indent=4
            )


# =========================================================
# Spotify / ReccoBeats 데이터 병합
# =========================================================

def combine(spotify_raw_data, reccobeats_raw_data):
    combine_raw_data =[]

    for track in spotify_raw_data:
        if not track:
            continue

        if track["spotify_id"] in reccobeats_raw_data:
            track.update(reccobeats_raw_data[track["spotify_id"]])
            combine_raw_data.append(track)
        

    return combine_raw_data


# =========================================================
# 음악 메타데이터 수집
# =========================================================
def spotify_search(query, token):
    try:
        spotify_result = spotify.search(query, token)
    except (Exception) as error:
        raise Etlerror("spotify", query, error)

    return spotify_result

def make(query, token):
    raw_data = []

    spotify_raw_data = []

    # Spotify: 곡 검색 및 기본 메타데이터 수집
    try:
        spotify_result = spotify.search(query, token)
    except (Exception) as error:
        raise Etlerror("spotify", query, error)


    data = spotify.match(query, spotify_result)
    spotify.append(data, spotify_raw_data)

    time.sleep(SPOTIFY_ACCESS_TIME_LIMIT)

    # ReccoBeats: BPM 및 음계 관련 데이터 수집
    try:
        reccobeats_raw_data = reccobeats.search(spotify_raw_data)
    except(Exception) as error:
        raise Etlerror("lastfm", query, error)
    
    combine_raw_data = combine(spotify_raw_data, reccobeats_raw_data)

    # Discogs 우선 검색, 실패 시 Last.fm으로 장르 보완
    for data in combine_raw_data:
        if not data:
            continue

        try:
            genre = discogs.search(data["artist"], data["track"])
        except(Exception):
            raise Etlerror("discongs", query, error)

        if not genre:
            genre = lastfm.search(data["artist"], data["track"])

        data["genre"] = genre

        time.sleep(1)

    raw_data.extend(combine_raw_data)

    return raw_data


# =========================================================
# 필수 메타데이터 검증
# =========================================================

def clean_raw_data(metadatas):
    required_keys = [
        "spotify_id",
        "artist",
        "track",
        "tempo",
        "key",
        "mode",
        "genre"
    ]

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

        if metadata["key"] is None or metadata["key"] == "":
            continue

        if metadata["mode"] is None:
            continue

        if not metadata["genre"]:
            continue

        cleaned.append(metadata)

    return cleaned


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

        batch = queries[0 : 10]

        batch_data = []
        for track in batch:
            token = spotify.get_access_token()

            try:    
                spotify_result = spotify_search(track, token)
                spotify_data = spotify.match(track, spotify_result)
            except:
                print("예외 발생 : track 보존")
                fail_track.append(track)

        del queries[0 : 10]
        raw_data.extend(batch_data)
        
    eliminate_duplicate_raw_data = []
    # Spotify ID 기준으로 중복 데이터 제거
    for metadata in raw_data:
        spotify_id = metadata["spotify_id"]

        if spotify_id in data["collected_spotify_id"]:
            continue

        eliminate_duplicate_raw_data.append(metadata)
        data["collected_spotify_id"][spotify_id] = True

        # 가수 + 곡명 기준 검색용 매핑 갱신
        normalized_title = normalize(
            metadata["artist"] + metadata["track"]
        )

        data["collected_track_title"][normalized_title] = True

        data["collected_track_and_spotify_id"][
            normalized_title
        ] = spotify_id

    # 기존 Raw Data에 신규 데이터 추가
    data["raw_data"].extend(eliminate_duplicate_raw_data)

    # 검색에 실패한 데이터 저장
    data["failed_data"].extend(fail_track)
    

    # 변경된 JSON 데이터 저장
    reload(data)

    return True
