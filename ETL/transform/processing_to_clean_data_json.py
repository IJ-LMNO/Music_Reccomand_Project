import json

def processing():

    with open("data/extract/raw_data.json", "r", encoding="utf-8") as raw_data, \
        open("data/common/normalize_genre_white_list.json", "r", encoding="utf-8") as whitelist, \
        open("data/commom/essential_key.json" ,"r", encoding="utf-8") as essential_key:
            
            raw_data = json.load(raw_data)
            whitelist = json.load(whitelist)
            essential_key = json.load(essential_key)

    clean_data = []
    for data in raw_data:

        # 필수 키/값 검사
        invalid = False

        for key in essential_key:
            if data.get(key) is None:
                invalid = True
                break

        if invalid:
            continue

        # 장르 필터링
        filter_genre = []

        for genre in data.get("genre", []):
            if genre in whitelist:
                filter_genre.append(genre)

        if len(filter_genre) == 0:
            continue

        data["genre"] = filter_genre

        clean_data.append(data)

    with open("data/transform/clean_data.json", "w", encoding="utf-8") as file:
        json.dump(clean_data, file, ensure_ascii=False, indent=4)
