import Processing_Bpm as bpm
import Processing_Genre as genre
import Processing_Spotify_id as id
import Processing_Track_name as track

def main():
    genre.Make_raw_Genre_dict()
    bpm.Processing_Bpm()
    id.Make_Track_index()
    track.Make_Track_index()

if __name__ == "__main__":
    main()