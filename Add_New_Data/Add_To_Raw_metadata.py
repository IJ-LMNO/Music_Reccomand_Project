import json

def Add_track_To_Raw_metadata(new_track):

    with open("Data/Raw_metadata.json", "r", encoding="utf-8") as file:
        rawdataset = json.load(file)

    rawdataset.extend(new_track)
    
    with open("Data/Bpm_dataset.json", "w", encoding="utf-8") as file:
        json.dump(rawdataset, file, ensure_ascii=False, indent=4)