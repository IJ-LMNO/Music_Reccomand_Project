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

def Make_Track_index():
    with open("Data/Clean_metadata.json", "r", encoding="utf-8") as clean_metadata:
        clean_metadata = json.load(clean_metadata)

    track_dataset = {}

    for metadata in clean_metadata:
        key = normalize(metadata["artist"] + metadata["track"])
        track_dataset[key] = metadata["spotify_id"]

    with open("Data/Track_name_index.json", "w", encoding="utf-8") as file:
        json.dump(track_dataset, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    Make_Track_index()