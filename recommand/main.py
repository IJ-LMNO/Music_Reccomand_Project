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

def recommend(input_track):
    after_bpm = bpm(input_track[0])
    after_genre = genre(input_track[0], after_bpm)
    after_chord = chord(input_track[0], after_genre)

    return after_chord


@app.post("/chat/question")
async def chat(request : Request):
    data = await request.json()
    after_recommend = []
    result = None

    with connect.cursor() as cur:
        try:
            if(data["mode"] == "song"):
                cur.execute("select * from clean_data where track = %s",data["message"])

                result = cur.fetchall()
                #같은 노래가 있어서 result가 여러개 리턴될 경우 처리
            else:
                ## 문장으로 처리된 경우 처리 -> llm 연동
                return "개발예정"

            if result is None:
                raise HTTPException(
                    status_code=404,
                    detail="에러 발생"
                )   
        except Exception as err:
            print(err)

        #recommend에 들어가는 노래는 한 곡으로 특정된 상황
        after_recommend = recommend(result)

        return after_recommend

        


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)