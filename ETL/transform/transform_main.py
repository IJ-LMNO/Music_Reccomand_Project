import Music_Reccomand_Project.make_dataset.Processsing_Raw_Data.Processing_Bpm as bpm
import Music_Reccomand_Project.make_dataset.Processsing_Raw_Data.Processing_Clean_metadata as cleanmetadata
import Music_Reccomand_Project.make_dataset.Processsing_Raw_Data.Processing_Spotify_id as id
import Music_Reccomand_Project.make_dataset.Processsing_Raw_Data.Processing_Track_name as track

def main():
    cleanmetadata.Make_clean_metadata()
    bpm.Processing_Bpm()
    id.Make_Track_index()
    track.Make_Track_index()

if __name__ == "__main__":
    main()