import json
import random

CHOOSE_RATIO = [0.7]


def Genre_layer(input_track, after_bpm_layer_track_arr,count, weight):
    output_track_arr = []
    track_select_by_Choose_ratio = []
    CHOOSE_RATIO.append(weight)

    total_track_num = count

    with open("Data/Constant_data/Genre_Toconomy_mapping.json", "r", encoding="utf-8") as file:
        genre_mapping = json.load(file)

    # 입력곡 세부 장르 파악
    specific_input_genre_arr = []

    for genre in input_track["genre"]:
        if genre in genre_mapping:
            specific_input_genre_arr.extend(genre_mapping[genre])

    specific_input_genre = set(specific_input_genre_arr)

    # 후보곡별 장르 유사도 계산
    for track in after_bpm_layer_track_arr:
        specific_tracks_genre_arr = []

        #각 트랙별 세부 장르 파악
        for genre in track["genre"]:
            if genre in genre_mapping:
                specific_tracks_genre_arr.extend(genre_mapping[genre])

        specific_track_genre = set(specific_tracks_genre_arr)



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

    # 1차, 2차 ratio 기준
    for pass_ratio in CHOOSE_RATIO:
        for item in track_select_by_Choose_ratio:
            if item["ratio"] >= pass_ratio:
                output_track_arr.append(item["track"])
                track_select_by_Choose_ratio.remove(item)

            if len(output_track_arr) >= total_track_num:
                print_tracks(output_track_arr)
                return output_track_arr

    # 3차: 공통 장르 1개 이상
    for item in track_select_by_Choose_ratio:
        if item["common_count"] >= 1:
            output_track_arr.append(item["track"])
            track_select_by_Choose_ratio.remove(item)

        if len(output_track_arr) >= total_track_num:
            print_tracks(output_track_arr)
            return output_track_arr

    # 그래도 부족하면 현재까지 랜덤으로 반환개수를 채워서 반환
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
