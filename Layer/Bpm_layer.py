import json
import random


# 곡 제목 검색을 위해 문자열을 소문자화하고 특수문자를 제거하는 정규화 함수
def normalize(text):
    return (
        text.lower()
        .replace(" ", "")
        .replace("-", "")
        .replace("!", "")
        .replace("'", "")
        .replace("(", "")
        .replace(")", "")
    )


import json
import random


# BPM 추천에 필요한 인덱스 및 데이터셋을 로드하는 함수
def load_bpm_data():
    with open("Data/Track_name_index.json", "r", encoding="utf-8") as track_name_index_file, \
         open("Data/Bpm_dataset.json", "r", encoding="utf-8") as bpm_dataset_file, \
         open("Data/Spotify_id_index.json", "r", encoding="utf-8") as track_index_file:

        track_name_index = json.load(track_name_index_file)
        bpm_dataset = json.load(bpm_dataset_file)
        track_index = json.load(track_index_file)

    return track_name_index, bpm_dataset, track_index


# 입력곡의 BPM 구간을 기준으로 유사한 템포의 후보곡을 선별하는 레이어
def Bpm_Layer(input_data, count):
    total_recommend_track = count
    input_track_metadata = None
    output_track_arr = []

    # 검색 인덱스, BPM 버킷 데이터, 전체 메타데이터 인덱스 로드
    track_name_index, bpm_dataset, track_index = load_bpm_data()

    # 사용자 입력곡 제목을 인덱스 검색용 형태로 정규화
    normalize_input_data = normalize(input_data)

    # 입력곡이 데이터셋에 없는 경우 추천 진행 불가
    if normalize_input_data not in track_name_index:
        print("해당 노래 없음")
        raise ValueError("해당 노래가 없습니다.")

    # 입력곡의 Spotify ID와 메타데이터 조회
    track_spotify_id = track_name_index[normalize_input_data]
    track_data = track_index[track_spotify_id]
    input_track_metadata = track_data

    # 입력곡 BPM을 10 단위 구간으로 변환
    same_bpm = int(track_data["tempo"] // 10) * 10

    # 같은 BPM 구간과 인접 BPM 구간 후보 조회
    same_bucket = bpm_dataset.get(str(same_bpm), [])
    plus_bucket = bpm_dataset.get(str(same_bpm + 10), [])
    minus_bucket = bpm_dataset.get(str(same_bpm - 10), [])

    # 자기 자신을 후보에서 먼저 제거
    same_bucket = [
        track for track in same_bucket
        if track["spotify_id"] != input_track_metadata["spotify_id"]
    ]

    plus_bucket = [
        track for track in plus_bucket
        if track["spotify_id"] != input_track_metadata["spotify_id"]
    ]

    minus_bucket = [
        track for track in minus_bucket
        if track["spotify_id"] != input_track_metadata["spotify_id"]
    ]

    # 1. 같은 BPM 구간에서 먼저 후보곡 선택
    if len(same_bucket) >= total_recommend_track:
        output_track_arr = random.sample(same_bucket, total_recommend_track)
        print_tracks(output_track_arr)
        return [input_track_metadata, output_track_arr]

    # 같은 BPM 구간 후보가 부족하면 우선 모두 추가
    output_track_arr.extend(same_bucket)

    lack_count = total_recommend_track - len(output_track_arr)

    # 부족한 개수는 전체 데이터셋에서 중복과 자기 자신을 제외하고 랜덤 보충
    if lack_count > 0:
        all_tracks = []

        for bucket in bpm_dataset.values():
            all_tracks.extend(bucket)

        already_ids = set(track["spotify_id"] for track in output_track_arr)
        already_ids.add(input_track_metadata["spotify_id"])

        random_candidates = [
            track for track in all_tracks
            if track["spotify_id"] not in already_ids
        ]

        if len(random_candidates) >= lack_count:
            output_track_arr.extend(random.sample(random_candidates, lack_count))
        else:
            output_track_arr.extend(random_candidates)

        print_tracks(output_track_arr)
        return [input_track_metadata, output_track_arr]


# BPM 레이어를 통과한 추천 결과 출력
def print_tracks(output_track_arr):
    print("after filtering bpm ->")
    for metadata in output_track_arr:
        print(metadata["artist"])
        print(metadata["track"])
        print(metadata["tempo"])
        print("--------------------------------")
        print()
    print()
    print()
    print()


if __name__ == "__main__":
    Bpm_Layer()