from common.normalize import normalize

import json
import random



# BPM 추천에 필요한 인덱스 및 데이터셋을 로드하는 함수
def load():
    with open("Data/Track_name_index.json", "r", encoding="utf-8") as track_name_index_file, \
         open("Data/Bpm_dataset.json", "r", encoding="utf-8") as bpm_dataset_file, \
         open("Data/Spotify_id_index.json", "r", encoding="utf-8") as track_index_file:

        track_name_index = json.load(track_name_index_file)
        bpm_dataset = json.load(bpm_dataset_file)
        track_index = json.load(track_index_file)

    return track_name_index, bpm_dataset, track_index


# 입력곡의 BPM 구간을 기준으로 유사한 템포의 후보곡을 선별하는 레이어
def layer(input_query, count = 30):
    min_required_tracks = count
    output_data = []

    # 검색 인덱스, BPM 버킷 데이터, 전체 메타데이터 인덱스 로드
    collected_track_title_and_spotify_id, dataset_by_spotify_id, dataset_by_bpm = load()

    # 사용자 입력곡 제목을 인덱스 검색용 형태로 정규화
    normalize_input_query = normalize(input_query)

    # 입력곡이 데이터셋에 없는 경우 추천 진행 불가
    ##@@ 입력곡이 없는 경우 etl을 수행하는 방향으로 진행
    if normalize_input_query not in collected_track_title_and_spotify_id:
        print("해당 노래 없음")
        raise ValueError("해당 노래가 없습니다.")

    # 입력곡의 Spotify ID와 메타데이터 조회
    # 입력곡 -> collected_track_title_and_spotify_id에서 키값 매칭으로 spotify_id 찾음
    # id를 통해 dataset_by_spotify_id에서 키값으로 매칭되는 노래를 찾음
    # 해당 노래의 bpm(tempo)를 가져옴
    spotify_id = collected_track_title_and_spotify_id[normalize_input_query]
    input_data = dataset_by_spotify_id[spotify_id]
    

    # 입력곡 BPM을 10 단위 구간으로 변환
    input_data_bpm = int(input_data["tempo"] // 10) * 10

    # 같은 BPM 구간과 인접 BPM 구간 후보 조회
    equal_bpm_bucket = dataset_by_bpm.get(str(input_data_bpm), [])
    high_bpm_bucket = dataset_by_bpm.get(str(input_data_bpm + 10), [])
    low_bpm_bucket = dataset_by_bpm.get(str(input_data_bpm - 10), [])

    # 자기 자신을 후보에서 먼저 제거
    equal_bpm_bucket = [
        track for track in equal_bpm_bucket
        if track["spotify_id"] != input_data["spotify_id"]
    ]

    # 같은 bpm에 맞는 데이터셋 선택
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
    return [input_data, output_data]
            