from flask import Flask, request, jsonify
from flask_cors import CORS

from Layer.Bpm_layer import Bpm_Layer as bpm
from Layer.Genre_layer import Genre_layer as genre
from Layer.Chord_layer import Chord_Layer as chord

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


if __name__ == "__main__":
    app.run(debug=True, port=5000)