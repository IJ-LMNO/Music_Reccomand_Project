import json

def Add_track_by_Spotify_id(new_track):
    with open("Data/Spotify_id_index.json", "r", encoding="utf-8") as file:
        track_index = json.load(file)

    track = new_track[0]

    track_index[track["spotify_id"]] = track

    with open("Data/Spotify_id_index.json", "w", encoding="utf-8") as file:
        json.dump(track_index, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    Add_track_by_Spotify_id()