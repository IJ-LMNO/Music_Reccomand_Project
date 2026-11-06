import uvicorn
import pymysql

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from layer.bpm.bpm_layer import layer as bpm
from layer.genre.genre_layer import layer as genre
from layer.chord.chrod_layer import layer as chord


DATABASE_URL = "localhost"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://192.168.131.128:5500",
        ],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["Content-Type"]
)

connect = pymysql.connect(
    host=DATABASE_URL,
    user="music",
    password='2323',
    database='music',
    cursorclass=pymysql.cursors.DictCursor
)

setting_value = {
    "recommendcount": 10, 
    "chordpenalty": 50, 
    "genrepenalty": 50
}

def recommend(input_track):
    #recommend에 들어온 input_track은 동일한 곡명이 여러개 있을 경우 하나로 특정해서 들어온 상태로 가정
    after_bpm = bpm(input_track, 
    setting_value["recommendcount"] * 5
    )

    after_genre = genre(
        input_track,
        after_bpm,
        setting_value["recommendcount"] * 4,
    )

    after_chord = chord(
        input_track,
        after_genre,
        setting_value["recommendcount"] *3,
    )

    return after_chord


@app.post("/setting")
async def setting(request : Request):
    data = await request.json()

    if  data:
        message = data["message"]


        setting_value["recommendcount"] = message["recommendCount"]
        setting_value["chordpenalty"] = message["chordPenalty"]
        setting_value["genrePenalty"] = message["genrePenalty"]


        return True
    else:
        return False

    




@app.post("/check")
async def check(request : Request):
    data = await request.json()
    result = None

    with connect.cursor() as cur:
        try:
            cur.execute("select * from clean_data where track = %s",data["message"])

            result = cur.fetchall()

            if result is None:
                raise HTTPException(
                    status_code=404,
                    detail="에러 발생"
                )  


        except Exception as err:
            print(err)



    return result


@app.post("/song")
async def chat(request : Request):
    data = await request.json()
    after_recommend = []

    #recommend에 들어가는 노래는 한 곡으로 특정된 상황
    after_recommend = recommend(data["message"])

    return after_recommend

        


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)