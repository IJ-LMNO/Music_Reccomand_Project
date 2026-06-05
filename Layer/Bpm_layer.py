import json
import random
from Make_Raw_Data import Main_API as Make_Raw_Data_API
from Add_New_Data import Add_New_Data_Main as Add_New_Data_Main



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



def load_bpm_data():
    with open("Data/Track_name_index.json", "r", encoding="utf-8") as track_name_index_file, \
         open("Data/Bpm_dataset.json", "r", encoding="utf-8") as bpm_dataset_file, \
         open("Data/Spotify_id_index.json", "r", encoding="utf-8") as track_index_file:

        track_name_index = json.load(track_name_index_file)
        bpm_dataset = json.load(bpm_dataset_file)
        track_index = json.load(track_index_file)

    return track_name_index, bpm_dataset, track_index


def Bpm_Layer(input_data, count):
    total_recommend_track = count
    input_track_metadata = None
    output_track_arr = []

    track_name_index, bpm_dataset, track_index = load_bpm_data()

    normalize_input_data = normalize(input_data)

    if normalize_input_data not in track_name_index:
        print("새로운 노래 추가 중")

        new_track = Make_Raw_Data_API.main(normalize_input_data)

        if new_track is None:
            print("해당 노래 없음")
            raise ValueError("해당 노래가 없습니다.")

        Add_New_Data_Main.Main(new_track, normalize_input_data)
        print("노래 추가 완료")

        # 새 노래가 JSON 파일에 추가되었으므로 다시 읽기
        track_name_index, bpm_dataset, track_index = load_bpm_data()

    track_spotify_id = track_name_index[normalize_input_data]
    track_data = track_index[track_spotify_id]
    input_track_metadata = track_data

    same_bpm = int(track_data["tempo"] // 10) * 10

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

    # 1. 같은 BPM 구간에서 먼저 가져오기
    if len(same_bucket) >= total_recommend_track:
        output_track_arr = random.sample(same_bucket, total_recommend_track)
        print_tracks(output_track_arr)
        return [input_track_metadata, output_track_arr]

    output_track_arr.extend(same_bucket)

    lack_count = total_recommend_track - len(output_track_arr)

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
