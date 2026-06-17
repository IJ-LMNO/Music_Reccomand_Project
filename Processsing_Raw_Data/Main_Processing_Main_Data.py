import Processing_Bpm as bpm
import Processing_Clean_metadata as cleanmetadata
import Processing_Spotify_id as id
import Processing_Track_name as track

def main():
    cleanmetadata.Make_clean_metadata()
    bpm.Processing_Bpm()
    id.Make_Track_index()
    track.Make_Track_index()

if __name__ == "__main__":
    main()