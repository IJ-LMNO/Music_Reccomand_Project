import json
import heapq

# 유사도 계산 시 상위 몇 %의 결과만 사용할지 결정하는 비율
CUTING_RATIO = 0.5


# Tonnetz 그래프에서 두 코드 사이의 최단 거리를 계산하는 함수
def dijkstra(graph, start, end):
    ENHARMONIC = {
        "C#": "Db",
        "D#": "Eb",
        "G#": "Ab",
        "A#": "Bb"
    }

    ##print------------------
    # print(start)
    ##-------------------
    start = ENHARMONIC.get(start, start)
    end = ENHARMONIC.get(end, end)

    # Tonnetz에 없는 코드면 비교 불가
    if start not in graph or end not in graph:
        return None

    distances = {node: float("inf") for node in graph}
    distances[start] = 0

    pq = [(0, start)]

    while pq:
        current_distance, current_node = heapq.heappop(pq)

        if current_node == end:
            return current_distance

        if current_distance > distances[current_node]:
            continue

        # 인접 코드들을 탐색하며 더 짧은 거리 발견 시 갱신
        for neighbor in graph[current_node]:
            neighbor = ENHARMONIC.get(neighbor, neighbor)

            if neighbor not in distances:
                continue

            new_distance = current_distance + 1

            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                heapq.heappush(pq, (new_distance, neighbor))

    return None


# Key와 Mode에 해당하는 대표 코드 진행 후보들을 실제 코드명으로 변환
def Make_number_of_chord_cases(Progression, chord, mode):

    number_of_chord_arr = []
    if(mode == "major"):
        mode_progresion = Progression["major_progressions"]
    else:
        mode_progresion = Progression["minor_progressions"]

    for case in mode_progresion:
        chord_arr = []
        for alpabet in case:
            chord_arr.append(chord[alpabet])
        number_of_chord_arr.append(chord_arr)

    return number_of_chord_arr


# 입력곡 코드 진행과 후보곡 코드 진행을 위치별로 비교하여 다른 코드 쌍만 추출
def Compare_note_proximity(input_track, tracks):
    return_arr = []

    for input_track_chord in input_track:
        chord_compare_result = []

        for track_chord in tracks:
            note_pairs = []

            for input_track_note, track_note in zip(input_track_chord, track_chord):
                if input_track_note == track_note:
                    continue

                note_pairs.append([input_track_note, track_note])

            chord_compare_result.append(note_pairs)

            # #--------------------------------------
            # print(chord_compare_result)
            # print()
            # #---------------------------------------

        return_arr.append(chord_compare_result)

    return return_arr


# 입력곡과 후보곡의 Key/Mode를 기준으로 가능한 코드 진행을 만들고,
# Tonnetz 그래프 거리 기반으로 코드 진행 유사도를 계산
def Compare_key_Progression(Progression, chords, tonnetz, input_track, track):
    input_track_mode = None
    track_mode = None

    KEY_MAP = {
        0: "C",
        1: "Db",
        2: "D",
        3: "Eb",
        4: "E",
        5: "F",
        6: "F#",
        7: "G",
        8: "Ab",
        9: "A",
        10: "Bb",
        11: "B"
    }

    # 입력곡의 Key/Mode 변환
    if input_track["mode"] == 0:
        input_track_mode = "minor"
        input_track_key = KEY_MAP[input_track["key"]] + "m"
    else:
        input_track_mode = "major"
        input_track_key = KEY_MAP[input_track["key"]]

    # 후보곡의 Key/Mode 변환
    if track["mode"] == 0:
        track_mode = "minor"
        track_key = KEY_MAP[track["key"]] + "m"
    else:
        track_mode = "major"
        track_key = KEY_MAP[track["key"]]

    # 입력곡과 후보곡에서 가능한 대표 코드 진행 후보 생성
    all_posstibilty_input_track_chord = Make_number_of_chord_cases(
        Progression,
        chords[input_track_mode][input_track_key],
        input_track_mode
    )

    all_posstibilty_track_chord = Make_number_of_chord_cases(
        Progression,
        chords[track_mode][track_key],
        track_mode
    )

    # 코드 진행 간 서로 다른 코드 쌍 추출
    chord_pair_arr = Compare_note_proximity(
        all_posstibilty_input_track_chord,
        all_posstibilty_track_chord
    )

    proximity_value = []

    for chord_pair in chord_pair_arr:
        if not track:
            continue

        # ##print------------------
        # print(chord_pair)
        # print()
        # ##-------------------

        sum = 0

        # 서로 다른 코드 쌍에 대해 Tonnetz 최단 거리 누적
        for track_pair in chord_pair:
            for pair in track_pair:
                if(len(track_pair) == 3):
                    distance = dijkstra(tonnetz, pair[0], pair[1])
                    if(distance == None):
                        distance = 10

                    sum = sum + distance
                else:
                    distance = dijkstra(tonnetz, pair[0], pair[1])

                    if(distance == None):
                        distance = 10

                    sum = sum + distance

                    for _ in range(0, 3 - len(track_pair)):
                        sum = sum + 0

        proximity_value.append(sum / 3)

    return proximity_value


# 여러 코드 진행 비교 결과 중 상위 일부만 사용하여 대표 유사도 점수 산출
def proximity_analze(simularity_chord_value_arr):

    rank_simularity = []

    for notes_arr in simularity_chord_value_arr:
        if not notes_arr:
            rank_simularity.append(float("inf"))
            continue

        notes_arr.sort()

        k = int(len(notes_arr) * CUTING_RATIO)
        if k < 1:
            k = 1

        useful_arr = notes_arr[:k]

        rank_simularity.append(sum(useful_arr) / len(useful_arr))

    return rank_simularity


# Key와 Mode 일치 여부에 따라 추천 점수에 보정값 적용
def Give_penalty(result, after_genre_layer, input_track, key, mode):
    return_result = []

    for track_proximity in result:
        track_idx = track_proximity[0]
        score = track_proximity[1]
        track = after_genre_layer[track_idx]

        new_score = score

        if input_track["mode"] == track["mode"]:
            new_score -= mode
        else:
            new_score += mode

        if input_track["key"] != track["key"]:
            new_score += key

        return_result.append(
            (
                track_idx,
                new_score
            )
        )

        #-----------------------
        print(return_result)
        print()
        #-------------------

    return return_result


# 코드 진행 기반 추천 레이어
# Tonnetz 거리, 코드 진행 유사도, Key/Mode 보정을 이용하여 후보곡을 선별
def Chord_Layer(input_track, after_genre_layer_track_arr, count, key_penalty=1, mode_penalty=1):
    total_return_track_num = count
    output_track = []

    # 코드 진행 비교에 필요한 고정 데이터 로드
    with open("Data/Constant_data/Tonnetz_Graph.json", "r", encoding="utf-8") as t,\
    open("Data/Constant_data/Representation_Progressions.json", "r", encoding="utf-8") as p,\
    open("Data/Constant_data/Key_Chords.json", "r", encoding="utf-8") as k:
            tonnetz = json.load(t)
            progression = json.load(p)
            chords = json.load(k)

    # 장르 레이어를 통과한 후보곡 전체에 대해 코드 진행 유사도 계산
    simularity_chord_value_arr = []
    for track in after_genre_layer_track_arr:
        simulairty = Compare_key_Progression(progression, chords, tonnetz, input_track, track)
        simularity_chord_value_arr.append(simulairty)

    # 각 후보곡의 대표 유사도 점수 계산
    total_simularity = proximity_analze(simularity_chord_value_arr)

    # 유사도 점수가 낮을수록 입력곡과 가까우므로 오름차순 정렬
    result = sorted(
        enumerate(total_simularity),
        key=lambda x: x[1]
    )

    # Key/Mode 기반 패널티 및 보너스 적용
    result = Give_penalty(result, after_genre_layer_track_arr, input_track, key_penalty, mode_penalty)

    # 최종 반환 개수만큼 후보곡 선택
    if len(result) < total_return_track_num:
        for i in range(len(result)):
            track_index_num = result[i][0]

            output_track.append(after_genre_layer_track_arr[track_index_num])

    else:
        for i in range(total_return_track_num):
            track_index_num = result[i][0]

            output_track.append(after_genre_layer_track_arr[track_index_num])

    print_tracks(output_track)
    return output_track


# 코드 진행 레이어를 통과한 추천 결과 출력
def print_tracks(output_track_arr):
    if not output_track_arr:
        print("empty")
    else:
        print("after filtering chord ->")
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
    Chord_Layer()