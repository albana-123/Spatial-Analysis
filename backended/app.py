from flask import Flask, request, jsonify
import openai
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
from flask_cors import CORS
import geojson
import re

app = Flask(__name__)
CORS(app)

openai.api_key = "YOUR_OPENAI_API_KEY"

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    analysis_type = data.get("analysisType", "").lower()
    question = data.get("question", "")
    features = data.get("features", [])

    try:
        geometries = [shape(f['geometry']) for f in features]

        if analysis_type == "buffer":
            match = re.search(r'(\d+)', question)
            dist = float(match.group(1)) if match else 100
            buffered = geometries[0].buffer(dist / 111320)
            return jsonify({"analysisGeoJSON": geojson.Feature(geometry=mapping(buffered))})

        elif analysis_type == "intersection":
            if len(geometries) < 2:
                return jsonify({"message": "Need at least two features for intersection."})
            result = geometries[0]
            for g in geometries[1:]:
                result = result.intersection(g)
            return jsonify({"analysisGeoJSON": geojson.Feature(geometry=mapping(result))})

        elif analysis_type == "union":
            result = unary_union(geometries)
            return jsonify({"analysisGeoJSON": geojson.Feature(geometry=mapping(result))})

        elif analysis_type == "gpt":
            prompt = f"""
You are a geospatial assistant using Shapely logic. The user has drawn {len(features)} GeoJSON features and wants to perform a spatial operation.

Features:
{geojson.dumps(features)}

User query: "{question}"

Analyze the request and return ONLY the final geometry as a valid GeoJSON Feature object.
Example response:
{{"type": "Feature", "geometry": {{ "type": "...", "coordinates": [...] }}, "properties": {{}} }}
"""

            completion = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = completion.choices[0].message['content']
            try:
                response_geojson = geojson.loads(response_text)
                return jsonify({"analysisGeoJSON": response_geojson})
            except Exception as e:
                return jsonify({"message": f"GPT response parse error: {e}", "raw": response_text})

        else:
            return jsonify({"message": "Invalid analysis type."})

    except Exception as e:
        return jsonify({"error": str(e)})