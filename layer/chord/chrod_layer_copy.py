import json
import heapq

#다익스트라 알고리즘
def dijkstra(
        graph, 
        start, 
        end
    ):

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

            if neighbor not in distances:
                continue

            new_distance = current_distance + 1

            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                heapq.heappush(pq, (new_distance, neighbor))

    return None

# 필요한 데이터 로드
def load():
    with open("chord/data/tonnetz_graph.json", "r", encoding="utf-8") as tonnetz,\
    open("chord/data/chord_to_notes.json", "r", encoding="utf-8") as notes,\
    open("chord/data/chord_progression_by_key_mode.json", "r", encoding="utf-8") as representative_chord,\
    open("chord/data/key_map.json", "r", encoding="utf-8") as spotify_key_map,\
    open("chord/data/progression_weight.json", "r", encoding="utf-8") as progression_weight,\
    open("chord/data/chord_to_roman.json", "r", encoding="utf-8") as chord_to_roman,\
    open("chord/data/genre_integration_mapping.json", "r", encoding="utf-8") as genre_integration_mapping:
        tonnetz = json.load(tonnetz) # tonnetz
        notes = json.load(notes) # chord_to_notes -> 각 코드를 구성하는 3개의 음
        representative_chord = json.load(representative_chord) # 각 음계별 나타날 수 있는 대표 코드 조합
        spotify_key_map = json.load(spotify_key_map) # 스포티파이에서 제공하는 key, mode 매핑표
        weight = json.load(progression_weight) # 각 코드 진행별 가중치
        roman = json.load(chord_to_roman) # 가중치 판단을 위해 코드 -> 로마자 표기법으로 바꾼 매핑표
        genre_integration = json.load(genre_integration_mapping)

    return tonnetz, notes, representative_chord, spotify_key_map, weight, roman, genre_integration

# mode + key를 통해 음계 및 음게의 대표 코드진행(3코드 진행 20개 4코드 진행 10개 추출)
def extract(
        track, # track
        representative_chord, # chord_progressions_by_key_mode.json -> 각 음계별 대표 3코드 진행 20개 4코드 진행 10개를 배열로 리턴
        spotify_key_map # key_map.json -> 스포티파이에서 제공하는 mode와 key를 매핑
    ):

    track_key_and_mode = []

    if str(track["mode"]) in spotify_key_map["mode"]:
        mode = spotify_key_map["mode"][str(track["mode"])]
        track_key_and_mode.append(mode)

    if str(track["key"]) in spotify_key_map["key"]:
        key = spotify_key_map["key"][str(track["key"])]
        track_key_and_mode.append(key)

    return [track_key_and_mode, representative_chord[track_key_and_mode[0]][track_key_and_mode[1]], track["genre"]]
    

def integreation(track_genre,
                       key_and_mode,
                       genre_integration, 
                       weight
                    ):
    chord_weight_progression = []
    integration_genre = []

    for genre in track_genre:
        integration_genre.append(genre_integration[genre])
    integration_genre = set(integration_genre)
    
    for genre in integration_genre:
        chord_weight_progression.append(weight[genre][key_and_mode[0]])
    
    return chord_weight_progression
    
def get_weight(chord_weight_progression, chord_progression_roman):
    weight_sum = 0
    weight_num = 0

    for progression in chord_weight_progression:
            weight_sum += progression.get("-".join(chord_progression_roman),1.0)
            weight_num += 1

    return weight_sum / weight_num


def switch_roman(chord_progression,key_and_mode, roman):
    chord_progression_roman = []
    for chord in chord_progression:
        chord_progression_roman.append(roman[key_and_mode[0]][key_and_mode[1]][chord])
    
    return chord_progression_roman



def comparison(
        track_info, # 입력된 곡의 정보 -> [[mode, key], [해당 음계 대표 코드 진행 30개]] 
        after_genre_track_info, # 장르 레이어를 거친 곡들 중 하나의 곡에 대한 정보 -> [[mode, key], [해당 음계 대표 코드 진행 30개]] 
        tonnetz, # 토네츠 표
        notes, # 각 코드를 구성하는 3개의 음
        weight, # 장르별 코드 진행에 대한 가중치
        roman, # 가중치 판단을 위해 코드 -> 로마자 표기법으로 바꾼 매핑표
        genre_integration
    ):

    comparison_value = 0 # 다익스트랑 * 가중치에 대한 값을 저장할 리스트 : 분자
    comparison_weight = 0 # 사용한 가중치를 저장할 리스트 : 분모

    track_key_and_mode = track_info[0]
    after_genre_track_key_and_mode = after_genre_track_info[0]

    track_chords_progression = track_info[1]
    after_genre_track_chords_progression = after_genre_track_info[1]

    track_genre = track_info[2]
    after_genre_track_genre = after_genre_track_info[2]

    # track에서의 장르별 weight 리스트 저장
    track_chord_weight_progression = integreation(track_genre, track_key_and_mode, genre_integration, weight)

    # 장르 레이어에서 거친 곡에 대한 weigth 리스트 저장
    after_genre_chord_weight_progression = integreation(after_genre_track_genre, after_genre_track_key_and_mode, genre_integration, weight)


    for track_chord_progression in track_chords_progression:
        track_chord_notes = []
        track_chord_notes_3 = [] # 30개의 대표 코드 진행 중 하나의 코드진행을 9개의 음표([[1,2,3],[4,5,6],[7,8,9]])로 바꿔 저장할 배열
        track_chord_notes_4 = []
        track_chord_progression_roman = [] # 30개의 대표 코드 진행 중 하나의 코드진행을 로마자로 변환할 리스트
        track_chord_weight = 1 # 30개의 대표 코드 진행 중 하나의 코드진행을 가중치로 변환해 저장할 리스트

        #로마자 변환
        track_chord_progression_roman = switch_roman(track_chord_progression, track_key_and_mode, roman)
        
        #변환한 로마자로 가중치 산출
        track_chord_weight = get_weight(track_chord_weight_progression, track_chord_progression_roman)

        # track_chord_progression을 3코드 진행 4코드 진행으로 확장 -> after_genre_track_chord의 길이와 다를 때를 대비
        # 3코드에서 4코드로 바꾸는 것이 아닌 애초에 4코드인 경우엔느 그냥 진행 : after_genre_track_chord를 바꿔야 하기 떄문에 여기서 조정해주지 않아도 됨
        if(len(track_chord_progression) == 3):
            track_chord_progression_3 = track_chord_progression
            track_chord_progressaion_4 = [track_chord_progression[0]] + track_chord_progression

            # 음표 리스트로 변환 -> 3코드 진행, 4코드 진행 모두 만들어 둠
            for chord in track_chord_progression_3:
                track_chord_notes_3.append(notes[chord])

            for chord in track_chord_progressaion_4:
                track_chord_notes_4.append(notes[chord])
        else:
            for chord in track_chord_progression:
                track_chord_notes.append(notes[chord])


        # 장르 레이어를 거쳐온 리스트에 대한 전처리
        for after_genre_chord_progression in after_genre_track_chords_progression:
            after_genre_chord_notes = [] # 30개의 대표 코드 진행 중 하나의 코드진행을 9개의 음표([[1,2,3],[4,5,6],[7,8,9]])로 바꿔 저장할 배열
            after_genre_chord_progression_roman = [] # 30개의 대표 코드 진행 중 하나의 코드진행을 로마자로 변환할 리스트
            after_genre_chord_weight = 1

            #로마자 변환
            after_genre_chord_progression_roman = switch_roman(after_genre_chord_progression, after_genre_track_key_and_mode, roman)

            #변환한 로마자로 가중치 산출
            after_genre_chord_weight = get_weight(after_genre_chord_weight_progression,after_genre_chord_progression_roman )


            # track_chord_progression과 after_genre_chord_progression간 코드 길이 조정
            if(len(track_chord_progression) == 3):
                if(len(after_genre_chord_progression) == 3):
                    final_track_chord_notes = track_chord_notes_3 
                elif(len(after_genre_chord_progression) == 4):
                    final_track_chord_notes = track_chord_notes_4
            else:
                if(len(after_genre_chord_progression) == 3):
                    final_track_chord_notes = track_chord_notes
                    after_genre_chord_progression = [after_genre_chord_progression[0]] + after_genre_chord_progression
                elif(len(after_genre_chord_progression) == 4):
                    final_track_chord_notes = track_chord_notes

            # 9개의 음표 리스트로 변환
            for chord in after_genre_chord_progression:
                after_genre_chord_notes.append(notes[chord]) # [[1,2,3],[4,5,6],[7,8,9]]

            # 각 곡을 이루는 30개의 코드들 중 하나에 대한 유사도 및 가중치 연산 진행
            distance_sum = 0
            distance_count = 0
            for track, after_genre in zip(final_track_chord_notes, after_genre_chord_notes):
                for track_note, after_genre_note in zip(track, after_genre):
                    distance = dijkstra(tonnetz, track_note, after_genre_note)

                    if distance is None:
                        return None

                    distance_sum += distance
                    distance_count += 1

            progression_distance = distance_sum / distance_count


            # track에 장르에 대한 가중치 계산 후 가중치, 연산값 저장
            comparison_value = comparison_value + (progression_distance * track_chord_weight * after_genre_chord_weight)
            comparison_weight = comparison_weight + (track_chord_weight * after_genre_chord_weight)

    return comparison_value / comparison_weight

# layer main
def layer(after_genre_layer, selected_ratio, count, key_penalty=1, mode_penalty=1):
    track = after_genre_layer[0] # 입력된 곡
    after_genre_track = after_genre_layer[1] # genre 계층을 통과한 곡들을
    ratio = selected_ratio
    min_required_tracks = count

    output_data = []

    tonnetz, notes, representative_chord, spotify_key_map, weight, roman, genre_integration = load()

    #검색된 노래의 [[mode, key], [해당 음계 대표 코드 진행 30개], 트랙의 장르] 
    track_info = extract(track, representative_chord, spotify_key_map)

    # genre layer를 통과한 노래들의 [[mode, key], [해당 음계 대표 코드 진행 30개], 트랙의 장르] 
    after_genre_layer_tracks_info = [] 
    for track in after_genre_track:
        after_genre_layer_tracks_info.append(extract(track, representative_chord, spotify_key_map ))


    #검색된 노래의 코드 및 모드와 genre layer를 통과한 각 노래들의 비교
    after_comparision = []
    idx = 0
    for after_genre_layer_track_info in after_genre_layer_tracks_info:
        comparison_result = comparison(track_info, after_genre_layer_track_info, tonnetz, notes, weight, roman, genre_integration)
        after_comparision.append([idx,comparison_result])
        idx += 1

    output_data = sorted(after_comparision, key=lambda x: x[1])

    return output_data[0:min_required_tracks]

