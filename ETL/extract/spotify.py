import base64
import requests
import time
import os

from dotenv import load_dotenv
from ETL.common.normalize import normalize



## Access Token 가상화 ======================================================================
##============================================================================
load_dotenv()
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
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
def search(query, batch, token, limit=10):
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
            },
            timeout=10
        )

    # 네트워크 연결 오류 및 Timeout
    except requests.exceptions.RequestException as error:
        batch.append(query)
        print(f"Spotify 연결 오류: {error}")
        return None

    # 정상 응답
    if res.status_code == 200:
        try:
            return res.json()
        except ValueError:
            batch.append(query)
            print("Spotify JSON 응답 오류")
            return None

    # API 호출 제한
    elif res.status_code == 429:
        batch.append(query)

        try:
            wait_time = max(1, int(res.headers.get("Retry-After", 10)))
        except ValueError:
            wait_time = 10

        extand_wait_time = wait_time + 10
        print(f"Spotify 요청 제한: {extand_wait_time}초 대기")
        
        time.sleep(extand_wait_time)
        return None

    # Spotify 서버 오류
    elif 500 <= res.status_code < 600:
        batch.append(query)
        print(f"Spotify 서버 오류: {res.status_code}")
        return None

    # 그 외 HTTP 오류는 원인 확인 필요
    else:
        res.raise_for_status()
        raise RuntimeError(f"예상하지 못한 응답: {res.status_code}")
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
            "spotify_id": data[0],
            "artist": data[1],
            "track": data[2]
        })
    else:
        raw_data.append([])
##============================================================================
##============================================================================       
        


