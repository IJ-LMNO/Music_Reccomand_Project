import base64
import requests
import time
import os

from dotenv import load_dotenv
from Music_Reccomand_Project.ETL.Extract.common.normalize import normalize



## Access Token 가상화 ======================================================================
##============================================================================
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
##============================================================================
##============================================================================





## 스포티파이 api 개발자 토큰 발급=============================================
##============================================================================
def get_access_token():
    auth = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_b64 = base64.b64encode(auth.encode()).decode()

    res = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={
            "grant_type": "client_credentials"
        }
    )

    res.raise_for_status()
    return res.json()["access_token"]
##============================================================================
##============================================================================




## 스포티파이에서 노래 검색======================================================================
##============================================================================
def search(query, token, limit=5):
    while True:
        res = requests.get(
            "https://api.spotify.com/v1/search",
            headers={
                "Authorization": f"Bearer {token}"
            },
            params={
                "q": query,
                "type": "track",
                "limit": limit
            }
        )

        if res.status_code == 429:
            wait_time = int(res.headers.get("Retry-After", 10))
            print(f"Spotify 요청 제한 발생: {wait_time}초 대기")
            time.sleep(wait_time)
            continue

        res.raise_for_status()
        return res.json()
##============================================================================
##============================================================================




## 스포티파이에서 노래 검색_copy======================================================================
##============================================================================
def search_spotify(query, token, limit=5):
    while True:
        try:
            res = requests.get(
                "https://api.spotify.com/v1/search",
                headers={
                    "Authorization": f"Bearer {token}"
                },
                params={
                    "q": query,
                    "type": "track",
                    "limit": limit
                }
            )
        except Exception:
            if res.status_code == 429:
                wait_time = int(res.headers.get("Retry-After", 10))
                print(f"Spotify 요청 제한 발생: {wait_time}초 대기")
                time.sleep(wait_time)
                continue

        res.raise_for_status()
        return res.json()
##============================================================================
##============================================================================






##검색된 값과 실제 값 비교========================================================================
##============================================================================
def match(query, return_query):
    normalized_query = normalize(query)
    items = return_query["tracks"]["items"]

    if not items:
        return []

    best_track = None
    best_score = 0

    for track in items:
        artist_name = track["artists"][0]["name"]
        track_name = track["name"]

        normalized_artist = normalize(artist_name)
        normalized_title = normalize(track_name)

        combined = normalized_artist + normalized_title
        query_without_artist = normalized_query.replace(normalized_artist, "")

        score = 0

        # 1. 가장 강한 조건: artist + title 완전 일치
        if normalized_query == combined:
            score = 100

        # 2. 입력 전체가 artist + title 안에 포함
        elif normalized_query in combined:
            score = 80

        # 3. artist가 입력에 있고, 제목 후보도 title과 맞음
        elif (
            normalized_artist in normalized_query
            and len(query_without_artist) >= 4
            and (
                query_without_artist in normalized_title
                or normalized_title in query_without_artist
            )
        ):
            score = 70

        # 4. 제목만 입력과 맞음
        elif (
            len(normalized_title) >= 4
            and normalized_title in normalized_query
        ):
            score = 50

        if score > best_score:
            best_score = score
            best_track = track

    # 너무 약한 매칭은 실패 처리
    if best_score < 70:
        return []

    return [
        best_track["id"],
        best_track["artists"][0]["name"],
        best_track["name"]
    ]


##raw_data에 append========================================================================
##============================================================================
def append(data, raw_data):
    if data:
        raw_data.append({
            "spotify_id": raw_data[0],
            "artist": raw_data[1],
            "track": raw_data[2]
        })
    else:
        raw_data.append([])
##============================================================================
##============================================================================       
        


