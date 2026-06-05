import json

def Add_track_in_dataset(query):
    with open("Make_Raw_Data/Dataset.json", "r", encoding="utf-8") as file:
        dataset = json.load(file)

        dataset.append(query)
    with open("Make_Raw_Data/Dataset.json", "w", encoding="utf-8") as file:
        json.dump(
            dataset,
            file,
            ensure_ascii=False,
            indent=4
        )