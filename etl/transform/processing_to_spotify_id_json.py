import json

def processing():

    with open("data/transform/clean_data.json", "r", encoding="utf-8") as clean_data:
        clean_data = json.load(clean_data)

    track_dataset = {}

    for data in clean_data:
        track_dataset[data["spotify_id"]] = data
    
    with open("data/transform/dataset_by_spotify.json", "w", encoding="utf-8") as file:
        json.dump(track_dataset, file, ensure_ascii=False, indent=4)
