import requests


def reccobeats():


    res = requests.get(
        "https://api.reccobeats.com/v1/audio-features",
        #["69BIczdH6QMnFx7dsSssN8", "7EyhPjrJzjx0fk2i7vUJCS"]
        params=[("ids", ["1rEa59P5yEal5cp1h7kl2e"])]
    )

    print(res.status_code)
    print(res.json())


if __name__ == "__main__":
    reccobeats()
