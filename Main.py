from flask import Flask, request, jsonify
from flask_cors import CORS

from Layer.Bpm_layer import Bpm_Layer as bpm
from Layer.Genre_layer import Genre_layer as genre
from Layer.Chord_layer import Chord_Layer as chord
from Layer.Weather_layer import Weather_Layer as weather

app = Flask(__name__)
CORS(app)


@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json()

    if data is None:
        return jsonify({
            "success": False,
            "message": "요청 데이터가 없습니다."
        }), 400

    track = data.get("track")
    count = data.get("count", 1)

    options = data.get("options", {})
    genre_weight = float(options.get("genreWeight", 0.5))
    key_penalty = float(options.get("keyPenalty", 0.15))
    mode_bonus = float(options.get("modeBonus", 0.1))

    if not track:
        return jsonify({
            "success": False,
            "message": "곡 이름을 입력하세요."
        }), 400

    try:
        count = int(count)

        bpm_count = 2 * count
        genre_count = int(1.5 * count)
        chord_count = count

        bpm_output_arr = bpm(track, bpm_count)

        genre_output_arr = genre(
            bpm_output_arr[0],
            bpm_output_arr[1],
            genre_count,
            genre_weight
        )

        chord_output_arr = chord(
            bpm_output_arr[0],
            genre_output_arr,
            chord_count,
            key_penalty,
            mode_bonus
        )

        return jsonify({
            "success": True,
            "input": bpm_output_arr[0],
            "recommendations": chord_output_arr
        }), 200

    except ValueError as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 404

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@app.route("/weather-recommend", methods=["POST"])
def weather_recommend():
    data = request.get_json()

    if data is None:
        return jsonify({
            "success": False,
            "message": "요청 데이터가 없습니다."
        }), 400

    recommendations = data.get("recommendations", [])

    if not recommendations:
        return jsonify({
            "success": False,
            "message": "날씨 추천에 사용할 추천곡 목록이 없습니다."
        }), 400

    try:
        weather_result = weather(
            recommendations,
            k=1,
            city="Seoul"
        )

        weather_playlist = weather_result.get("weather_playlist", [])

        if len(weather_playlist) == 0:
            return jsonify({
                "success": True,
                "weather": weather_result.get("weather"),
                "weather_recommendation": None,
                "message": "날씨 기반 추천 결과가 없습니다."
            }), 200

        return jsonify({
            "success": True,
            "weather": weather_result.get("weather"),
            "weather_recommendation": weather_playlist[0]
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)