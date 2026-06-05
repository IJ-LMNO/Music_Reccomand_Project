import json


def Make_raw_Genre_dict():

    with open("Data/Raw_metadata.json", "r", encoding="utf-8") as file_rawdata,\
        open("Data/Constant_data/Normalize_Genre_Whitelist.json", "r", encoding="utf-8") as file_whitelist:
        rawdata = json.load(file_rawdata)
        whitelist = json.load(file_whitelist)
        

        for track_metadata in rawdata:
            filter_genre = []

            for genre in track_metadata["genre"]:

                if genre in whitelist:
                    filter_genre.append(genre)
                else:
                    continue
            
            track_metadata["genre"] = filter_genre

    with open("Data/Clean_metadata.json", "w", encoding="utf-8") as file:
        json.dump(rawdata, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    Make_raw_Genre_dict()