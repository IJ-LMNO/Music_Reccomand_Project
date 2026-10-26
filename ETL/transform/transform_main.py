import transform.processing_to_clean_data_json as clean_data
import transform.processing_to_bpm_json as bpm
import transform.processing_to_spotify_id_json as spotify_id

from multiprocessing import Pool

def main():
    clean_data.processing()

    with Pool(processes= 2)as pool:
        bpm_pool_result = pool.apply_async(bpm.processing)
        spotify_id_pool_result = pool.apply_async(spotify_id.processing)

        bpm_pool_result.get()
        spotify_id_pool_result.get()

    return True

