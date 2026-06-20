과제4 기말프로젝트 알고리즘 조사
202235239 김지환

[프로젝트명]
음악 추천 시스템

[실행 환경]
Python 3.x

[필요 라이브러리]
flask
flask-cors
requests

설치 명령어:
pip install -r requirements.txt

[실행 방법]
프로젝트 최상위 폴더에서 아래 명령어 실행

python Main.py

[데이터 출처]

Spotify API
ReccoBeats API
Discogs API
Last.fm API

수집 데이터를 전처리하여 JSON 형태로 저장 후 사용


[폴더 구조]
Main.py
Layer/                   추천 레이어 코드
Data/                    음악 데이터 및 인덱스 JSON
Data/Constant_data/       Tonnetz, 코드 진행, 장르 whitelist JSON
templates/               웹 화면 파일

[실행 과정]
Main.py로 진입
frontend HTML 파일을 통해 음악 검색

[주의사항]
사용하는 여러 API의 토큰 제공이 불가능한 관계로, 일부 기능을 막아두었기 때문에
반드시 음악 검색 시 Track_name_index.json의 키 값 중 하나로 검색해야 함

--------------------------------------------------------------------------------

Requirement

flask,
flask-cors,
requests
