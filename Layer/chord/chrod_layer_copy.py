import json
import heapq

# 필요한 데이터 로드
def load():
    with open("chord/data/tonnetz_graph.json", "r", encoding="utf-8") as tonnetz,\
    open("chord/data/key_chord_notes.json", "r", encoding="utf-8") as notes,\
    open("chord/data/chord_progression_by_key_mode.json", "r", encoding="utf-8") as representative_chord,\
    open("chord/data/key_map.json", "r", encoding="utf-8") as spotify_key_map:
        tonnetz = json.load(tonnetz)
        notes = json.load(notes)
        representative_chord = json.load(representative_chord)
        spotify_key_map = json.load(spotify_key_map)

    return tonnetz, notes, representative_chord, spotify_key_map

# mode + key를 통해 음계 및 음게의 대표 코드진행(3코드 진행 20개 4코드 진행 10개 추출)
def representative_chord_by_spotify_chord_and_mode(
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

    return [track_key_and_mode, representative_chord[track_key_and_mode[0]][track_key_and_mode[1]]]
    

def dijkstra(graph, start, end):

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


def comparison(track_info, after_genre_layer_track_info, tonnetz, notes):

    track_key_and_mode = track_info[0]
    after_genre_layer_track_key_and_mode = after_genre_layer_track_info[0]

    track_chords = track_info[1]
    after_genre_layer_track_chords = after_genre_layer_track_info[1]

    # for track_chord in track_chords:
    #     for after_genre_layer_track_chord in after_genre_layer_track_chords:


     


# layer main
def layer(after_genre_layer, selected_ratio, count, key_penalty=1, mode_penalty=1):
    track_data = after_genre_layer[0] # 입력된 곡
    input_data = after_genre_layer[1] # genre 계층을 통과한 곡들을
    ratio = selected_ratio
    min_required_tracks = count

    output_data = []

    tonnetz, notes, representative_chord, spotify_key_map = load()

    #검색된 노래의 [[mode, key], [해당 음계 대표 코드 진행 30개]] 
    track_info = representative_chord_by_spotify_chord_and_mode(track, representative_chord, spotify_key_map)

    # genre layer를 통과한 노래들의 [[mode, key], [해당 음계 대표 코드 진행 30개]] 
    after_genre_layer_tracks_info = [] 
    for track in input_data:
        after_genre_layer_tracks_info.append(representative_chord_by_spotify_chord_and_mode(track, representative_chord, spotify_key_map ))


    #검색된 노래의 코드 및 모드와 genre layer를 통과한 각 노래들의 비교
    after_comparision = []
    for after_genre_layer_track_info in after_genre_layer_tracks_info:
        after_comparision = comparison(track_info, after_genre_layer_track_info, tonnetz, notes)



