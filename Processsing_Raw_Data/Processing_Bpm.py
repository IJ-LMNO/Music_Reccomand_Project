import json

def Processing_Bpm():

    with open("Data/Clean_metadata.json", "r", encoding="utf-8") as cleandata:
        cleandata = json.load(cleandata)

    bpmdataset = {}
    seen = set()

    for track in cleandata:
        spotify_id = track["spotify_id"]

        if spotify_id in seen:
            continue

        seen.add(spotify_id)

        tempo = int(track["tempo"])
        processing_bpm = (tempo // 10) * 10

        if processing_bpm not in bpmdataset:
            bpmdataset[processing_bpm] = []

        bpmdataset[processing_bpm].append(track)

    with open("Data/Bpm_dataset.json", "w", encoding="utf-8") as file:
        json.dump(bpmdataset, file, ensure_ascii=False, indent=4)