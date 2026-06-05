from Layer.Bpm_layer import Bpm_Layer as bpm
from Layer.Genre_layer import Genre_layer as genre
from Layer.Chord_layer import Chord_Layer as chord

def Main():
    track =  "taylorswiftcruelsummer"
    count = 3
    bpm_count = 3 *count
    genre_count = int(2*count)
    genre_weight = 0.3
    key_penalty = 0.3
    mode_penalty = 0.3

    bpm_output_arr = bpm(track,bpm_count)
    genre_output_arr = genre(bpm_output_arr[0], bpm_output_arr[1],genre_count,genre_weight)
    chord_output_arr = chord(bpm_output_arr[0], genre_output_arr, count, key_penalty, mode_penalty)


if __name__ == "__main__":
    Main()