import json

def Make_Track_index():

    with open("Data/Clean_metadata.json", "r", encoding="utf-8") as clean_metadata:
        clean_metadata = json.load(clean_metadata)

    track_dataset = {}

    for metadata in clean_metadata:
        track_dataset[metadata["spotify_id"]] = metadata

    with open("Data/Spotify_id_index.json", "w", encoding="utf-8") as file:
        json.dump(track_dataset, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    Make_Track_index()