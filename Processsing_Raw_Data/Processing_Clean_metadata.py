import json

def Make_clean_metadata():

    with open("Data/Raw_metadata.json", "r", encoding="utf-8") as file_rawdata, \
         open("Data/Constant_data/Normalize_Genre_Whitelist.json", "r", encoding="utf-8") as file_whitelist:

        rawdata = json.load(file_rawdata)
        whitelist = json.load(file_whitelist)

    clean_metadata = []
    seen = set()

    required_keys = [
        "spotify_id",
        "artist",
        "track",
        "tempo",
        "key",
        "mode",
        "energy",
        "danceability",
        "valence",
        "acousticness"
    ]

    for track_metadata in rawdata:

        # 필수 키/값 검사
        invalid = False

        for key in required_keys:
            if track_metadata.get(key) is None:
                invalid = True
                break

        if invalid:
            continue

        # spotify_id 중복 제거
        spotify_id = track_metadata["spotify_id"]

        if spotify_id in seen:
            continue

        seen.add(spotify_id)

        # 장르 필터링
        filter_genre = []

        for genre in track_metadata.get("genre", []):
            if genre in whitelist:
                filter_genre.append(genre)

        if len(filter_genre) == 0:
            continue

        track_metadata["genre"] = filter_genre

        clean_metadata.append(track_metadata)

    with open("Data/Clean_metadata.json", "w", encoding="utf-8") as file:
        json.dump(clean_metadata, file, ensure_ascii=False, indent=4)

    print("Raw Track Count:", len(rawdata))
    print("Clean Track Count:", len(clean_metadata))
    print("Removed Count:", len(rawdata) - len(clean_metadata))