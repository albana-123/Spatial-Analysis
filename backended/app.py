from flask import Flask, request, jsonify
import openai
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
from flask_cors import CORS
import geojson
import re

app = Flask(__name__)
CORS(app)

# Replace with your real OpenAI key
openai.api_key = "YOUR_OPENAI_API_KEY"

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    analysis_type = data.get("analysisType", "").lower()
    question = data.get("question", "")
    features = data.get("features", [])
    building_features = data.get("buildingFeatures", [])
    landuse_features = data.get("landuseFeatures", [])

    try:
        geometries = [shape(f['geometry']) for f in features]

        # ========== BUFFER ==========
        if analysis_type == "buffer":
            match = re.search(r'(\d+)', question)
            dist = float(match.group(1)) if match else 100
            buffer_geom = geometries[0].buffer(dist / 111320)  # degrees

            # Filter buildings inside buffer
            matched_buildings = []
            for b in building_features:
                b_geom = shape(b['geometry'])
                if buffer_geom.intersects(b_geom):
                    matched_buildings.append(b)

            # Filter landuse inside buffer
            matched_landuse = []
            for l in landuse_features:
                l_geom = shape(l['geometry'])
                if buffer_geom.intersects(l_geom):
                    matched_landuse.append(l)

            return jsonify({
                "analysisGeoJSON": geojson.FeatureCollection(
                    [geojson.Feature(geometry=mapping(buffer_geom), properties={"type": "buffer"})] +
                    matched_buildings +
                    matched_landuse
                )
            })

        # ========== INTERSECTION ==========
        elif analysis_type == "intersection":
            if len(geometries) < 2:
                return jsonify({"message": "Need at least two features for intersection."})
            result = geometries[0]
            for g in geometries[1:]:
                result = result.intersection(g)
            return jsonify({"analysisGeoJSON": geojson.Feature(geometry=mapping(result))})

        # ========== UNION ==========
        elif analysis_type == "union":
            result = unary_union(geometries)
            return jsonify({"analysisGeoJSON": geojson.Feature(geometry=mapping(result))})

        # ========== GPT-POWERED ==========
        elif analysis_type == "gpt":
            prompt = f"""
You are a geospatial assistant using Python Shapely logic. The user has drawn {len(features)} GeoJSON features.

User question:
"{question}"

GeoJSON features:
{geojson.dumps(features)}

If relevant, incorporate filtering of buildings or land use zones. 
Return ONLY a single valid GeoJSON Feature or FeatureCollection.
Don't explain anything—just return the JSON.
"""

            completion = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = completion.choices[0].message['content']
            try:
                parsed_geojson = geojson.loads(response_text)
                return jsonify({"analysisGeoJSON": parsed_geojson})
            except Exception as e:
                return jsonify({"message": f"GPT response error: {e}", "raw": response_text})

        else:
            return jsonify({"message": "Invalid analysis type."})

    except Exception as e:
        return jsonify({"error": str(e)})