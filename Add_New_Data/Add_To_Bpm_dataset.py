import json

def Add_track_by_BPM(new_track):

    with open("Data/Bpm_dataset.json", "r", encoding="utf-8") as file:
        bpmdataset = json.load(file)

    bpm = new_track[0]["tempo"]
    processing_bpm = int((bpm // 10) * 10)
    processing_bpm = str(processing_bpm)
    bpmdataset[processing_bpm].append(new_track[0])



    with open("Data/Bpm_dataset.json", "w", encoding="utf-8") as file:
        json.dump(bpmdataset, file, ensure_ascii=False, indent=4)