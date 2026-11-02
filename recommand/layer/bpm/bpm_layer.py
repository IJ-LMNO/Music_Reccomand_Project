import json
import random
import pymysql

from layer.common.normalize import normalize

connect = pymysql.connect(
    user="music",
    password="2323",
    database="music",
    cursorclass=pymysql.cursors.DictCursor

)

def load(input_track):
    cur = connect.cursor()

    equal_bpm_bucket = None
    high_bpm_bucket = None
    low_bpm_bucket = None

    bpm = (input_track["tempo"] // 10) * 10
    high_bpm = bpm + 10
    low_bpm = bpm - 10

    try:
        cur.execute(
            "SELECT * FROM clean_data WHERE tempo >= %s AND tempo < %s + 10",
            (bpm, bpm)
        )
        equal_bpm_bucket = cur.fetchall()

        cur.execute(
            "SELECT * FROM clean_data WHERE tempo >= %s AND tempo < %s + 10",
            (high_bpm, high_bpm)
        )
        high_bpm_bucket = cur.fetchall()

        cur.execute(
            "SELECT * FROM clean_data WHERE tempo >= %s AND tempo < %s + 10",
            (low_bpm, low_bpm)
        )
        low_bpm_bucket = cur.fetchall()
    except Exception as err:
        print("bpm bucket 생성 중 에러 발생 : ",err)
        raise ValueError("해당 노래가 없습니다. : 개발 예정")
        # 데이터베이스에 없는 노래를 입력한 경우 -> etl에 api요청 후 조회해야 함
        # 추후 개발 예정

    cur.close()
    return low_bpm_bucket, equal_bpm_bucket, high_bpm_bucket



def filter(low_bpm_bucket, equal_bpm_bucket, high_bpm_bucket, min_required_tracks):
    output_data = []

    if len(equal_bpm_bucket) >= min_required_tracks:
        output_data = random.sample(equal_bpm_bucket, min_required_tracks)
        return output_data
    else:
        lack_required_track = min_required_tracks - len(equal_bpm_bucket)
        output_data.extend(equal_bpm_bucket)

        num_for_high = random.randint(1, lack_required_track)
        num_for_low = lack_required_track - num_for_high


        if(num_for_high <= len(high_bpm_bucket) and num_for_low <= len(low_bpm_bucket)):
            high_bpm_data = random.sample(high_bpm_bucket, num_for_high)
            low_bpm_data = random.sample(low_bpm_bucket, num_for_low)

            output_data.extend(high_bpm_data + low_bpm_data)

        else:
            combine_bucket = high_bpm_bucket + low_bpm_bucket

            if(lack_required_track > len(combine_bucket)):
                output_data.extend(combine_bucket)
            else:
                output_data.extend(random.sample(combine_bucket, lack_required_track))

    #@@현재는 지정된 equal, high, low bucket을 탐색하고도 값이 없으면 bucket을 반환하는 구조
    #@@ 3개 BPM 버킷을 탐색한 후에도 최소 요구 곡 수를 충족하지 못하는 경우에 대한 예외 처리 정책 수립이 필요할 수도
    return output_data

# 입력곡의 BPM 구간을 기준으로 유사한 템포의 후보곡을 선별하는 레이어
def layer(input_track, count = 1):
    low_bpm_bucket, equal_bpm_bucket, high_bpm_bucket = load(input_track)

    # 자기 자신을 후보에서 먼저 제거
    # equal_bpm_bucket = [
    #     track for track in equal_bpm_bucket
    #     if track["spotify_id"] != input_track["spotify_id"]
    # ]

    # 같은 bpm에 맞는 데이터셋 선택
    after_filtering = filter(low_bpm_bucket, equal_bpm_bucket, high_bpm_bucket, count)

    return after_filtering

            