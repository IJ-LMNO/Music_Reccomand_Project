import json
import os
import pymysql

from pathlib import Path
from dotenv import load_dotenv
from common.normalize import normalize

DATABASE_URL = "localhost"

connect = pymysql.connect(
    host=DATABASE_URL,
    user="music",
    password="2323",
    database="music",
    cursorclass=pymysql.cursors.DictCursor,
)

load_dotenv()

# 실제 파일 경로로 변경
CLEAN_DATA = Path("data/transform/clean_data.json")

# 실제 테이블 이름으로 변경
TABLE_NAME = "clean_data"

COLUMNS = [
    "spotify_id",
    "artist",
    "track",
    "id",
    "href",
    "isrc",
    "acousticness",
    "danceability",
    "energy",
    "instrumentalness",
    "key",
    "liveness",
    "loudness",
    "mode",
    "speechiness",
    "tempo",
    "valence",
    "genre",
    "normalize"
]


def load():
    # Clean Data 불러오기
    with open(CLEAN_DATA, "r", encoding="utf-8") as f:
        data = json.load(f)

    # INSERT 쿼리 생성
    columns = ", ".join(f"`{column}`" for column in COLUMNS)
    placeholders = ", ".join(["%s"] * len(COLUMNS))

    sql = f"""
        INSERT INTO `{TABLE_NAME}` ({columns})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE
            `spotify_id` = `spotify_id`
    """

    # INSERT 데이터 준비
    rows = []

    for track in data:

        genre = track.get("genre")

        if genre is not None:
            genre = json.dumps(genre, ensure_ascii=False)

        row = (
            track["spotify_id"],
            track["artist"],
            track["track"],
            track.get("id"),
            track.get("href"),
            track.get("isrc"),
            track.get("acousticness"),
            track.get("danceability"),
            track.get("energy"),
            track.get("instrumentalness"),
            track.get("key"),
            track.get("liveness"),
            track.get("loudness"),
            track.get("mode"),
            track.get("speechiness"),
            track.get("tempo"),
            track.get("valence"),
            genre,
            normalize(track["artist"] + track["track"])
        )

        rows.append(row)

    cursor = connect.cursor()

    try:
        cursor.executemany(sql, rows)
        connect.commit()

        print(f"Load 완료: {cursor.rowcount}개 행 반영")

    except Exception:
        connect.rollback()
        raise

    finally:
        cursor.close()
        connect.close()


if __name__ == "__main__":
    load()
    