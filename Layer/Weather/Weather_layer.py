import os
import math
import heapq

try:
    import requests
except Exception:
    requests = None

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


FEATURE_ORDER = ["tempo", "energy", "danceability", "valence", "acousticness"]

TEMPO_MIN = 60.0
TEMPO_MAX = 180.0


WEATHER_PROFILES = {
    "Rain": {
        "target": [0.35, 0.30, 0.45, 0.30, 0.75],
        "rules": {
            "acousticness": +0.30,
            "energy": -0.20,
            "valence": -0.10
        },
    },
    "Snow": {
        "target": [0.30, 0.25, 0.40, 0.50, 0.70],
        "rules": {
            "acousticness": +0.25,
            "energy": -0.25,
            "danceability": -0.10,
            "valence": +0.05
        },
    },
    "Clear": {
        "target": [0.70, 0.80, 0.75, 0.80, 0.20],
        "rules": {
            "energy": +0.30,
            "danceability": +0.20,
            "valence": +0.20
        },
    },
    "Clouds": {
        "target": [0.50, 0.45, 0.50, 0.45, 0.50],
        "rules": {
            "acousticness": +0.10,
            "energy": -0.05,
            "valence": -0.05
        },
    },
}

DEFAULT_PROFILE_KEY = "Clouds"


TEMPERATURE_BANDS = {
    "cold": {
        "delta_target": [-0.10, -0.15, -0.05, -0.05, +0.15],
        "delta_rules": {
            "acousticness": +0.10,
            "energy": -0.10
        },
    },
    "cool": {
        "delta_target": [-0.05, -0.07, -0.02, -0.02, +0.07],
        "delta_rules": {
            "acousticness": +0.05,
            "energy": -0.05
        },
    },
    "mild": {
        "delta_target": [0.0, 0.0, 0.0, 0.0, 0.0],
        "delta_rules": {},
    },
    "warm": {
        "delta_target": [+0.05, +0.07, +0.05, +0.05, -0.05],
        "delta_rules": {
            "danceability": +0.05,
            "energy": +0.05
        },
    },
    "hot": {
        "delta_target": [+0.10, +0.12, +0.10, +0.08, -0.10],
        "delta_rules": {
            "danceability": +0.10,
            "energy": +0.10
        },
    },
}


OWM_CONDITION_MAP = {
    "Rain": "Rain",
    "Drizzle": "Rain",
    "Thunderstorm": "Rain",

    "Snow": "Snow",

    "Clear": "Clear",

    "Clouds": "Clouds",

    "Mist": "Clouds",
    "Fog": "Clouds",
    "Haze": "Clouds",
    "Smoke": "Clouds",
    "Dust": "Clouds",
    "Sand": "Clouds",
    "Ash": "Clouds",

    "Squall": "Rain",
    "Tornado": "Rain",
}


def _clamp(value, min_value=0.0, max_value=1.0):
    return max(min_value, min(max_value, value))


def normalize_tempo(tempo):
    return _clamp((tempo - TEMPO_MIN) / (TEMPO_MAX - TEMPO_MIN))


def temperature_band(temp_celsius):
    if temp_celsius is None:
        return "mild"

    if temp_celsius < 5:
        return "cold"

    if temp_celsius < 15:
        return "cool"

    if temp_celsius < 23:
        return "mild"

    if temp_celsius < 30:
        return "warm"

    return "hot"


def cosine_similarity(vector_a, vector_b):
    dot = 0.0
    norm_a = 0.0
    norm_b = 0.0

    for a, b in zip(vector_a, vector_b):
        dot += a * b
        norm_a += a * a
        norm_b += b * b

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return dot / (math.sqrt(norm_a) * math.sqrt(norm_b))


class WeatherLayer:
    OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(
        self,
        api_key=None,
        cosine_weight=0.5,
        rule_weight=0.5,
        units="metric"
    ):
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
        self.cosine_weight = cosine_weight
        self.rule_weight = rule_weight
        self.units = units

        self.weather_profiles = WEATHER_PROFILES
        self.temperature_bands = TEMPERATURE_BANDS
        self.condition_map = OWM_CONDITION_MAP

    def fetch_current_weather(self, city="Seoul", lat=None, lon=None):
        if requests is None:
            raise RuntimeError("requests 모듈이 없어 OpenWeather 호출이 불가능합니다.")

        if not self.api_key:
            raise RuntimeError("OPENWEATHER_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")

        params = {
            "appid": self.api_key,
            "units": self.units
        }

        if city:
            params["q"] = city
        elif lat is not None and lon is not None:
            params["lat"] = lat
            params["lon"] = lon
        else:
            params["q"] = "Seoul"

        response = requests.get(
            self.OPENWEATHER_URL,
            params=params,
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        raw_condition = data["weather"][0]["main"]

        return {
            "condition": self._map_condition(raw_condition),
            "raw_condition": raw_condition,
            "temp": data["main"]["temp"],
            "description": data["weather"][0].get("description", ""),
            "city": data.get("name", city),
            "source": "openweather"
        }

    def _map_condition(self, openweather_condition):
        return self.condition_map.get(openweather_condition, DEFAULT_PROFILE_KEY)

    def build_weather_profile(self, condition, temp=None):
        base_profile = self.weather_profiles.get(
            condition,
            self.weather_profiles[DEFAULT_PROFILE_KEY]
        )

        band = temperature_band(temp)
        temp_adjust = self.temperature_bands.get(
            band,
            self.temperature_bands["mild"]
        )

        target = []

        for i in range(len(FEATURE_ORDER)):
            adjusted_value = base_profile["target"][i] + temp_adjust["delta_target"][i]
            target.append(_clamp(adjusted_value))

        rules = dict(base_profile["rules"])

        for feature, weight in temp_adjust.get("delta_rules", {}).items():
            rules[feature] = rules.get(feature, 0.0) + weight

        return {
            "condition": condition,
            "band": band,
            "temp": temp,
            "target": target,
            "rules": rules
        }

    def extract_features(self, song):
        """
        네 프로젝트 데이터 구조 기준:
        audio_features 중첩 구조를 사용하지 않고,
        song 최상위 키에서 바로 읽는다.

        필요한 키:
        - tempo
        - energy
        - danceability
        - valence
        - acousticness

        위 feature가 없으면 tempo/mode 기반 추정값을 사용한다.
        """

        required_features = [
            "energy",
            "danceability",
            "valence",
            "acousticness"
        ]

        if all(feature in song for feature in required_features):
            return {
                "tempo": normalize_tempo(song.get("tempo", 120.0)),
                "energy": _clamp(song.get("energy", 0.5)),
                "danceability": _clamp(song.get("danceability", 0.5)),
                "valence": _clamp(song.get("valence", 0.5)),
                "acousticness": _clamp(song.get("acousticness", 0.5)),
            }

        return self._proxy_features(song)

    def _proxy_features(self, song):
        tempo_value = normalize_tempo(song.get("tempo", 120.0))
        is_major = song.get("mode", 1) == 1

        energy = _clamp(
            0.25 + 0.60 * tempo_value + (0.10 if is_major else 0.0)
        )

        danceability = _clamp(
            0.30 + 0.50 * tempo_value
        )

        valence = _clamp(
            (0.65 if is_major else 0.35) + 0.15 * (tempo_value - 0.5)
        )

        acousticness = _clamp(
            1.0 - 0.80 * energy
        )

        return {
            "tempo": tempo_value,
            "energy": energy,
            "danceability": danceability,
            "valence": valence,
            "acousticness": acousticness,
        }

    def _feature_vector(self, features):
        return [features[name] for name in FEATURE_ORDER]

    def rule_based_score(self, features, rules):
        raw_score = 0.0
        max_possible = 0.0
        min_possible = 0.0

        for feature, weight in rules.items():
            value = features.get(feature, 0.0)

            raw_score += weight * value

            if weight > 0:
                max_possible += weight
            else:
                min_possible += weight

        score_range = max_possible - min_possible

        if score_range == 0.0:
            return 0.5

        return _clamp((raw_score - min_possible) / score_range)

    def weather_score(self, song, profile):
        features = self.extract_features(song)
        vector = self._feature_vector(features)

        cosine_score = cosine_similarity(vector, profile["target"])
        rule_score = self.rule_based_score(features, profile["rules"])

        final_score = (
            self.cosine_weight * cosine_score
            + self.rule_weight * rule_score
        )

        return final_score, {
            "cosine": cosine_score,
            "rule": rule_score,
            "features": features
        }

    def rank_by_weather(self, songs, profile, k):
        heap = []

        for index, song in enumerate(songs):
            score, parts = self.weather_score(song, profile)

            payload = dict(song)

            payload["weather_score"] = round(score * 100, 1)
            payload["weather_score_raw"] = round(score, 4)

            payload["weather_score_detail"] = {
                "cosine": round(parts["cosine"], 4),
                "rule": round(parts["rule"], 4)
            }

            payload["weather_features"] = {
                "tempo": round(parts["features"]["tempo"], 4),
                "energy": round(parts["features"]["energy"], 4),
                "danceability": round(parts["features"]["danceability"], 4),
                "valence": round(parts["features"]["valence"], 4),
                "acousticness": round(parts["features"]["acousticness"], 4)
            }

            if len(heap) < k:
                heapq.heappush(heap, (score, index, payload))
            elif score > heap[0][0]:
                heapq.heapreplace(heap, (score, index, payload))

        result = [item[2] for item in heap]
        result.sort(key=lambda song: song["weather_score_raw"], reverse=True)

        return result

    def run(
        self,
        final_recommendations,
        k=1,
        city="Seoul",
        lat=None,
        lon=None,
        weather_override=None
    ):
        if not final_recommendations:
            return {
                "weather": None,
                "weather_profile": None,
                "weather_playlist": [],
                "original_recommendations": final_recommendations
            }

        if weather_override:
            raw_condition = weather_override.get("condition", DEFAULT_PROFILE_KEY)

            if raw_condition in self.weather_profiles:
                condition = raw_condition
            else:
                condition = self._map_condition(raw_condition)

            weather = {
                "condition": condition,
                "raw_condition": raw_condition,
                "temp": weather_override.get("temp"),
                "description": "manual override",
                "city": city,
                "source": "override"
            }
        else:
            weather = self.fetch_current_weather(
                city=city,
                lat=lat,
                lon=lon
            )

        profile = self.build_weather_profile(
            weather["condition"],
            weather["temp"]
        )

        k = min(k, len(final_recommendations))

        weather_playlist = self.rank_by_weather(
            final_recommendations,
            profile,
            k
        )

        return {
            "weather": weather,
            "weather_profile": profile,
            "weather_playlist": weather_playlist,
            "original_recommendations": final_recommendations
        }


def Weather_Layer(
    final_recommendations,
    k=1,
    city="Seoul",
    lat=None,
    lon=None,
    weather_override=None,
    cosine_weight=0.5,
    rule_weight=0.5
):
    layer = WeatherLayer(
        cosine_weight=cosine_weight,
        rule_weight=rule_weight
    )

    return layer.run(
        final_recommendations=final_recommendations,
        k=k,
        city=city,
        lat=lat,
        lon=lon,
        weather_override=weather_override
    )
