import json
import random


def load():
    with open("genre/data/genre_toconomy_mapping.json", "r", encoding="utf-8") as file:
        genre_toconomy_mapping = json.load(file)

    return genre_toconomy_mapping

# BPM 레이어를 통과한 후보곡 중 입력곡과 장르가 유사한 곡을 선별하는 레이어
def layer(after_bpm_layer, count, selected_ratio):
    track_data = after_bpm_layer[0] # 입력된 곡
    input_data = after_bpm_layer[1] # bpm 계층을 통과한 곡들을 저장한 list
    ratio = [0.7, selected_ratio]
    min_required_tracks = count



    # 상위 장르를 세부 장르 목록으로 확장하기 위한 매핑 데이터 로드
    genre_toconomy_mapping = load()



    # 입력곡의 장르를 세부 장르 집합으로 변환
    specific_genre_track_data = []
    for genre in track_data["genre"]:
        if genre in genre_toconomy_mapping:
            specific_genre_track_data.extend(genre_toconomy_mapping[genre])
    specific_genre_track_data = set(specific_genre_track_data)




    # 후보곡별 장르 유사도 계산
    input_data_genre_similarity_ratio = []
    input_data_idx = 0
    for track in input_data:
        specific_genre_input_data_track = []

        # 각 후보곡의 장르를 세부 장르 집합으로 변환
        for genre in track["genre"]:
            if genre in genre_toconomy_mapping:
                specific_genre_input_data_track.extend(genre_toconomy_mapping[genre])
        specific_genre_input_data_track = set(specific_genre_input_data_track)

        # 입력곡 장르와 후보곡 장르의 교집합 비율 계산
        input_genre = set(specific_genre_input_data_track)
        track_genre = set(specific_genre_track_data)

        denominator = len(input_genre | track_genre)
        numerator = len(input_genre & track_genre)

        # 자카드 유사도 계산
        similarity_ratio = numerator / denominator if denominator else 0

        #input_data_genre_similarity_ratio에 튜플 형식으로 저장
        input_data_genre_similarity_ratio.append((similarity_ratio, input_data_idx))

        input_data_idx += 1

    # input_data_genre_similarity_ratio 튜플의 첫번째 인덱스로 정렬
    input_data_genre_similarity_ratio.sort(key= lambda x :x [0], reverse=True)

    # 1차: 유사도 0.7 이상인 곡 선택
    selected_tracks = [
        track for track in input_data_genre_similarity_ratio
        if track[0] >= ratio[0]
    ]

    # 2차: 최소 요구 곡 수를 충족하지 못하면 사용자가 지정한 유사도 이상인 곡 선택
    if len(selected_tracks) < min_required_tracks:
        selected_tracks = [
            track for track in input_data_genre_similarity_ratio
                if track[0] >= ratio[1]
        ]

    # 3차: 2차에서도 만족하지 못하면 유사도가 높은 순서로 개수를 채워서 반환
    if len(selected_tracks) < min_required_tracks:

        lack_tracks_num = min_required_tracks - len(selected_tracks)
        selected_tracks.extend(input_data_genre_similarity_ratio[len(selected_tracks) : len(selected_tracks) + lack_tracks_num])

    # selected_data는 (유사도, input_data 인덱스)를 값으로 가지는 input_data_genre_similarity_ratio에서 만들어진 list
    # (유사도, input_data 인덱스)를 이용해 input_data에서 track을 가져와 output_data를 만들어야 함
    output_data = []
    for i in selected_tracks:
        idx = i[0]
        output_data.append(input_data[idx]) 


    return output_data


    
