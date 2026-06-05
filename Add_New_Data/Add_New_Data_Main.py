from Add_New_Data import Add_To_Bpm_dataset as Bpm
from Add_New_Data import Add_To_Clean_metadata as Genre
from Add_New_Data import Add_To_Spotify_id_index as Track_id
from Add_New_Data import Add_To_Track_name_index as Track_name
from Add_New_Data import Add_To_dataset as Dataset
from Add_New_Data import Add_To_Raw_metadata as Raw

def Add_New_Data_Main(new_track, query):

    Raw.Add_track_To_Raw_metadata(new_track)
    Dataset.Add_track_in_dataset(query)
    Genre.Add_To_Clean_Metadata(new_track)
    Bpm.Add_track_by_BPM(new_track)
    Track_id.Add_track_by_Spotify_id(new_track)
    Track_name.Add_track_by_Track_name(new_track,query)

if __name__ == "__main__":
    Add_New_Data_Main()