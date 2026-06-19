import json
import random

# 장르 유사도 판단에 사용할 기본 통과 기준
CHOOSE_RATIO = [0.7]


# BPM 레이어를 통과한 후보곡 중 입력곡과 장르가 유사한 곡을 선별하는 레이어
def Genre_layer(input_track, after_bpm_layer_track_arr, count, weight):
    output_track_arr = []
    track_select_by_Choose_ratio = []

    # 사용자가 설정한 장르 유사도 기준을 추가
    CHOOSE_RATIO.append(weight)

    total_track_num = count

    # 상위 장르를 세부 장르 목록으로 확장하기 위한 매핑 데이터 로드
    with open("Data/Constant_data/Genre_Toconomy_mapping.json", "r", encoding="utf-8") as file:
        genre_mapping = json.load(file)

    # 입력곡의 장르를 세부 장르 집합으로 변환
    specific_input_genre_arr = []

    for genre in input_track["genre"]:
        if genre in genre_mapping:
            specific_input_genre_arr.extend(genre_mapping[genre])

    specific_input_genre = set(specific_input_genre_arr)

    # 후보곡별 장르 유사도 계산
    for track in after_bpm_layer_track_arr:
        specific_tracks_genre_arr = []

        # 각 후보곡의 장르를 세부 장르 집합으로 변환
        for genre in track["genre"]:
            if genre in genre_mapping:
                specific_tracks_genre_arr.extend(genre_mapping[genre])

        specific_track_genre = set(specific_tracks_genre_arr)

        # 입력곡 장르와 후보곡 장르의 교집합 비율 계산
        if len(specific_input_genre) == 0:
            ratio = 0
        else:
            common_genre = specific_input_genre & specific_track_genre
            ratio = len(common_genre) / len(specific_input_genre)

        track_select_by_Choose_ratio.append({
            "track": track,
            "ratio": ratio,
            "common_count": len(specific_input_genre & specific_track_genre)
        })

    # 1차, 2차 기준: 장르 유사도 ratio 기준으로 후보곡 선별
    for pass_ratio in CHOOSE_RATIO:
        for item in track_select_by_Choose_ratio:
            if item["ratio"] >= pass_ratio:
                output_track_arr.append(item["track"])
                track_select_by_Choose_ratio.remove(item)

            if len(output_track_arr) >= total_track_num:
                print_tracks(output_track_arr)
                return output_track_arr

    # 3차 기준: 공통 장르가 1개 이상인 후보곡 선별
    for item in track_select_by_Choose_ratio:
        if item["common_count"] >= 1:
            output_track_arr.append(item["track"])
            track_select_by_Choose_ratio.remove(item)

        if len(output_track_arr) >= total_track_num:
            print_tracks(output_track_arr)
            return output_track_arr

    # 기준을 만족하는 곡이 부족하면 중복을 제외한 나머지 후보에서 랜덤으로 반환 개수 보충
    less_amount = total_track_num - len(output_track_arr)

    if len(output_track_arr) < total_track_num:
        exist_id = set(track["spotify_id"] for track in output_track_arr)

        candidates = []

        for track in after_bpm_layer_track_arr:
            track_id = track["spotify_id"]

            if track_id in exist_id:
                continue

            candidates.append(track)
            exist_id.add(track_id)

        if len(candidates) <= less_amount:
            output_track_arr.extend(candidates)
        else:
            output_track_arr.extend(random.sample(candidates, less_amount))

        print_tracks(output_track_arr)
        return output_track_arr


# 장르 레이어를 통과한 추천 결과 출력
def print_tracks(output_track_arr):
    if not output_track_arr:
        print("empty")
    else:
        print("after filtering genre ->")
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
    Genre_layer()