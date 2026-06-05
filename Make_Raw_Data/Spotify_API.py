import base64
import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

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


def normalize(text):
    return (
        text.lower()
        .replace(" ", "")
        .replace("-", "")
        .replace("!", "")
        .replace("'", "")
        .replace("(", "")
        .replace(")", "")
        .replace(".", "")
        .replace(",", "")
    )


def search_spotify(query, token, limit=5):
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


# def query_match(query, returnjson):
#     normalized_query = normalize(query)
#     items = returnjson["tracks"]["items"]

#     if not items:
#         return []

#     for track in items:
#         artist_name = track["artists"][0]["name"]
#         track_name = track["name"]

#         normalized_artist = normalize(artist_name)
#         normalized_title = normalize(track_name)

#         combined = normalized_artist + normalized_title

#         # 입력값에서 artist 이름을 제거해서 title 후보 추출
#         query_without_artist = normalized_query.replace(normalized_artist, "")

#         full_match = normalized_query == combined

#         title_match = (
#             query_without_artist
#             and (
#                 query_without_artist in normalized_title
#                 or normalized_title in query_without_artist
#             )
#         )

#         if full_match or title_match:
#             return [
#                 track["id"],
#                 artist_name,
#                 track_name
#             ]

#     return []

def query_match(query, returnjson):
    normalized_query = normalize(query)
    items = returnjson["tracks"]["items"]

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

def Spotify_API(query, metadatas, token):

    data = search_spotify(query, token, limit=5)
    metadata = query_match(query, data)

    if metadata:
        metadatas.append({
            "spotify_id": metadata[0],
            "artist": metadata[1],
            "track": metadata[2]
        })
    else:
        metadatas.append({})


