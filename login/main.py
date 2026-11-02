import uvicorn
import os
import pymysql
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware


connect = pymysql.connect(
   host='localhost',
   user='users_service',
   password='2323',
   database='users_service',
   cursorclass=pymysql.cursors.DictCursor
)


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["Content-Type"]
)


@app.post("/login/")
async def login(request : Request):
    data = await request.json()
    result = None

    try:
        with connect.cursor() as cur:
            cur.execute(f"SELECT id, password FROM users WHERE id = %s", (data["id"]))

            result = cur.fetchone()
    except Exception as err:
        print("조회 실패",err)


    if result is None:
        return {"success": False}

    if data["password"] == result["password"]:
        print("true")
        return {"success": True}
    else:
        return {"success": False}
        
@app.post("/member/")
async def memeber(request : Request):
    data = request.json()

    with connect.cursor() as cur:
        try:
            cur.execute(f"INSERT INTO users(id, password) VALUES('%s', '%s)", (data["id"], data["password"]))

            return True
        except Exception as error:
            print("회원 가입 실패 : ",error)

            return False

        




if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)