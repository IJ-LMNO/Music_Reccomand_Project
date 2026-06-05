import requests


def MusicBrainz_API(artist, track):

    res = requests.get(
        "https://musicbrainz.org/ws/2/recording/",
        params={
            "query": f'artist:{artist} AND recording:{track}',
            "fmt": "json"
        },
        headers={
            "User-Agent": "MusicRecommendationProject/1.0"
        }
    )

    print(f"status : {res.status_code}")



if __name__ == "__main__":

    data = MusicBrainz_API(
        "BLACKPINK",
        "How do you like that"
    )
