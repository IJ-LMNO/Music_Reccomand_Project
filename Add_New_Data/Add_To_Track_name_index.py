import json

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

def Add_track_by_Track_name(new_track, query):
    with open("Data/Track_name_index.json", "r", encoding="utf-8") as file:
        track_name_index = json.load(file)


    print(new_track[0])
    track_name_index[query] = new_track[0]["spotify_id"]

    with open("Data/Track_name_index.json", "w", encoding="utf-8") as file:
        json.dump(track_name_index, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    Add_track_by_Track_name()