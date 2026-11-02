# 음악 추천 코드 진행 데이터 v1 (2026-10-16)

## 구성
- `chord_progressions_by_key_mode.json`: Spotify 12개 Key × 장조/단조 2개 = 24개 음계 각각에 30개 실제 코드 진행 배열(3코드 20개 다음 4코드 10개). 전체 720개.
- `roman_progressions.json`: Key와 무관한 로마 숫자 진행 배열. 3코드 20개/4코드 10개, 장조·단조별.
- `progression_weights.json`: 로마 숫자 진행, 권장 가중치(휴리스틱), 종류 및 관련 자료 URL.
- `progression_weight_lookup.json`: 진행 패턴 문자열을 바로 가중치로 조회하는 사전. 예: `weights["major"]["I-V-VI-IV"]`.
- `key_chords.json`: Key/Mode별 7개의 기본 3화음 이름.
- `key_chord_notes.json`: 7개의 기본 3화음을 구성하는 개별 음들 (Tonnetz 음 거리 계산용).
- `spotify_key_map.json`: Spotify key = 0~11 → 음 이름.

## 호출 예
```python
mode = 'minor' if track['mode'] == 0 else 'major'
key = key_map[str(track['key'])]
progressions = chord_progressions[mode][key]
# 처음 20개는 3코드, 뒤의 10개는 4코드
```

## 엄밀한 해석과 주의
1. 음악 이론상 장조 기본 코드 I, ii, iii, IV, V, vi, vii°, 자연단음계 기본 코드 i, ii°, III, iv, v, VI, VII. JSON 로마 숫자 `I`~`VII`는 **숫자 위치만 표시**하고, 대문자가 메이저 코드란 뜻이 아님. 코드의 장조·단조 여부는 `key_chords.json`의 `m`, `dim`에 나타남. 기존 프로젝트의 로마 숫자 키 형식을 보존하기 위함.
2. 이 30개는 **실제 음악 전체를 집계한 '빈도 순위 1~30위'가 아님**. Hooktheory의 직접 사례/대표 패턴과 이론적으로 타당한 확장 후보를 합친 **큐레이션된 후보 리스트**. `progression_weights.json`의 `category`를 참고.
3. 가중치(1.0~1.65)는 **모델 초기값으로 제안한 휴리스틱**이지 논문에서 검증한 발생 확률이나 정량적 측정값이 아님. 실제 빈도에 비례한 가중치가 필요하다면 Hooktheory API, McGill Billboard 같은 자료로 동일한 집계 규칙을 정해 다시 계산해야 함.
4. 단조는 **자연단음계의 7개 3화음으로 제한**. 실제 대중음악에서 흔한 장조 V(예: Am 음계에서 E) 등 자연단음계 밖 코드는 **일부러 제외**했으므로, 특히 단조의 대표성에는 한계가 있음. 필요할 때 화성단음계에서 유래한 V를 옵션으로 추가.
5. 코드명은 음악 이론에 맞게 표기했으므로 `E#dim`, `Cb`, `C#m` 등 이명동음 표기가 발생. Spotify key=1(Db)의 단조는 같은 높이의 C# 단조 표기, key=8(Ab)의 단조는 G# 단조 표기를 사용. Tonnetz 그래프를 12음 이름으로 구성했다면 `pitch class`로 변환/정규화 후 비교해야 함.
6. Key와 Mode만으로 확보 가능한 정보 범위 내에서 코드 진행 후보를 생성. 이 파일의 목표는 코드 진행 후보 점수화에 활용하는 것.
7. `key_chords.json`는 기존 프로젝트의 단조 key 이름 `Cm` 등이 아니라 **major/minor 모두 Spotify Key(예: `C`, `Db`)를 사용**. 따라서 `key_chords[mode][key_map[str(key)]]`로 접근할 것. 기존 `key_chords[mode]["Cm"]` 접근은 변경 필요.
8. 3코드와 4코드의 점수 규모를 다르게 다루지 않도록 각 진행 거리를 코드 개수로 나눈 뒤 가중치를 적용. 3↔4 간 비교는 길이 차이 페널티 등 별도 정책 필요.
9. 모든 코드는 기본 3화음(3음)이며, `3코드 진행`과 `4코드 진행`은 **코드의 개수**임.

## 공개 참고 자료
- Hooktheory: 대중음악 1300곡 분석, I–V–vi–IV가 가장 많이 등장하는 4코드 진행이라고 보고: https://api.hooktheory.com/blog/music-theory-analysis-1300-songs-for-songwriting-part2/
- Hooktheory: 단조에서 흔한 코드 및 실제 곡의 코드 진행 사례, 자연단음계 외 장조 V 설명: https://api.hooktheory.com/blog/minor-chord-progressions/
- Hooktheory: 음계별 기본 3화음 및 코드 설명: https://api.hooktheory.com/support/musicreference?concept=music-concepts-basic-chord
- McGill Billboard 연구 데이터셋(740곡) – 추후 실제 코드 진행 빈도 분석 시 이용: https://ddmal.ca/research/The_McGill_Billboard_Project_(Chord_Analysis_Dataset)/
- Hooktheory Trends: 코드 진행의 연결 확률과 실제 음악 사례 검색: https://www.hooktheory.com/trends

## 추천 가중치 적용
최종 비교에 포함된 진행 쌍마다 distance `d_i`, 해당 진행 쌍의 중요도 `w_i`를 정의:
    final_distance = sum(w_i * d_i) / sum(w_i)
가중치는 노래별로 측정된 값이 아니고 패턴 단위 prior임.
서로 다른 진행 p,q를 비교할 때는 `w_pair = sqrt(w[p] * w[q])` (하나의 추천안)을 쓸 수 있으나, 어느 진행 쌍들을 집계할지부터 먼저 결정해야 한다.


##파일별 역할