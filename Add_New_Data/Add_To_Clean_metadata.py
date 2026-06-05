import json


def Add_To_Clean_Metadata(new_track):
    with open("Data/Constant_data/Normalize_Genre_Whitelist.json", "r", encoding="utf-8") as file_whitelist:
        whitelist = json.load(file_whitelist)

    # genre가 없거나 빈 경우 대비
    genres = new_track[0]["genre"]
    print(f"track : {genres}")

    filter_genre = []

    for genre in genres:
        if genre in whitelist:
            filter_genre.append(genre)

    new_track[0]["genre"] = filter_genre

    with open("Data/Clean_metadata.json", "r", encoding="utf-8") as file:
        old_data = json.load(file)

    old_data.extend(new_track)

    with open("Data/Clean_metadata.json", "w", encoding="utf-8") as file:
        json.dump(
            old_data,
            file,
            ensure_ascii=False,
            indent=4
        )

    return new_track
