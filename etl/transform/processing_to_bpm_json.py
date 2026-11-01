import json

def processing():

    with open("data/transform/clean_data.json", "r", encoding="utf-8") as clean_data:
        clean_data = json.load(clean_data)

    bpm_dataset = {}

    for track in clean_data:
        tempo = track.get("tempo")

        if tempo is None:
            continue

        try:
            tempo = int(tempo)
        except (TypeError, ValueError):
            continue

        processing_bpm = (tempo // 10) * 10

        if processing_bpm not in bpm_dataset:
            bpm_dataset[processing_bpm] = []

        bpm_dataset[processing_bpm].append(track)

    with open("data/transform/dataset_by_bpm.json", "w", encoding="utf-8") as file:
        json.dump(bpm_dataset, file, ensure_ascii=False, indent=4)