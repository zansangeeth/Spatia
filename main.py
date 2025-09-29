# import json
# import re
#
# import requests
# from fastapi import FastAPI, Request
# from fastapi.responses import HTMLResponse, JSONResponse
# from fastapi.staticfiles import StaticFiles
# from pydantic import BaseModel
# from typing import List, Dict, Any
#
# # Load GeoJSON once at startup
# with open("data1.geojson", "r") as f:
#     geojson_data = json.load(f)
#
# app = FastAPI(title="Local GeoJSON AI Agent")
#
#
# # Pydantic model for request body
# class QuestionRequest(BaseModel):
#     question: str
#
#
# # Simple HTML frontend
# HTML_TEMPLATE = """
# <!doctype html>
# <html>
# <head><title>Local GeoJSON AI Agent</title></head>
# <body>
#   <h2>Ask about your GeoJSON (LLM runs locally!)</h2>
#   <form id="questionForm">
#     <input type="text" id="question" name="question" placeholder="e.g., List all feature names" style="width:400px;" required>
#     <button type="submit">Ask</button>
#   </form>
#   <div id="answer" style="margin-top:20px; padding:10px; background:#e6f7ff; border-radius:5px;"></div>
#
#   <script>
#   document.getElementById('questionForm').onsubmit = async (e) => {
#     e.preventDefault();
#     const question = document.getElementById('question').value;
#     document.getElementById('answer').innerHTML = "Thinking...";
#
#     const response = await fetch('/ask', {
#       method: 'POST',
#       headers: {'Content-Type': 'application/json'},
#       body: JSON.stringify({question: question})
#     });
#     const data = await response.json();
#
#     if (data.values) {
#       // Show as a scrollable list
#       const listHtml = `
#         <strong>${data.answer}</strong>
#         <ul style="max-height:300px; overflow-y:auto; margin-top:10px;">
#           ${data.values.map(v => `<li>${v}</li>`).join('')}
#         </ul>
#       `;
#       document.getElementById('answer').innerHTML = listHtml;
#     } else {
#       document.getElementById('answer').innerText = data.answer;
#     }
#   };
# </script>
# </body>
# </html>
# """
#
#
# def ask_local_llm(prompt: str, model: str = "llama3") -> str:
#     """Send prompt to Ollama running on localhost"""
#     url = "http://localhost:11434/api/generate"
#     payload = {
#         "model": model,
#         "prompt": prompt,
#         "stream": False,
#         "options": {
#             "temperature": 0.3
#         }
#     }
#     try:
#         response = requests.post(url, json=payload, timeout=120)
#         if response.status_code == 200:
#             return response.json().get("response", "No response")
#         else:
#             return f"Error: HTTP {response.status_code}"
#     except Exception as e:
#         return f"Failed to connect to Ollama: {str(e)}"
#
#
# @app.get("/", response_class=HTMLResponse)
# async def home():
#     return HTMLResponse(content=HTML_TEMPLATE)
#
# def summarize_geojson(geojson: Dict[str, Any]) -> str:
#     """Convert GeoJSON into a human-readable summary for the LLM."""
#     if geojson.get("type") != "FeatureCollection":
#         return "The GeoJSON is not a FeatureCollection."
#
#     features = geojson.get("features", [])
#     if not features:
#         return "The GeoJSON contains no features."
#
#     summary_lines = [f"Total features: {len(features)}"]
#
#     # Analyze common properties
#     all_props = [f.get("properties", {}) for f in features]
#     if all_props:
#         # Get all unique property keys
#         prop_keys = set()
#         for p in all_props:
#             prop_keys.update(p.keys())
#
#         summary_lines.append(f"Common properties: {sorted(prop_keys)}")
#
#         # Show sample values (first 3 features)
#         for i, props in enumerate(all_props[:3]):
#             summary_lines.append(f"Feature {i + 1} properties: {props}")
#
#         if len(features) > 3:
#             summary_lines.append(f"... and {len(features) - 3} more features.")
#
#     return "\n".join(summary_lines)
#
# def extract_all_property_values(geojson: Dict[str, Any], prop_name: str) -> List[str]:
#     """Extract all values of a given property from GeoJSON features."""
#     values = []
#     for feature in geojson.get("features", []):
#         props = feature.get("properties", {})
#         if prop_name in props:
#             values.append(props[prop_name])
#     return values
#
# @app.post("/ask")
# async def ask(request: QuestionRequest):
#     user_question = request.question.strip()
#
#     # 🔍 Check if the question asks to list all values of a property
#     # Example: "give me all 'areanm' values", "list all areanm"
#     prop_match = re.search(r"all\s+['\"]?(\w+)['\"]?\s+.*valu", user_question, re.IGNORECASE)
#     if not prop_match:
#         prop_match = re.search(r"list\s+.*['\"]?(\w+)['\"]?", user_question, re.IGNORECASE)
#
#     if prop_match:
#         prop_name = prop_match.group(1)
#         all_values = extract_all_property_values(geojson_data, prop_name)
#         if all_values:
#             return JSONResponse(content={
#                 "answer": f"Found {len(all_values)} values for property '{prop_name}':",
#                 "values": all_values  # Send as JSON array
#             })
#         else:
#             return JSONResponse(content={
#                 "answer": f"No values found for property '{prop_name}'."
#             })
#
#     # 🧠 Otherwise, use LLM for reasoning questions
#     geo_summary = summarize_geojson(geojson_data)
#     prompt = f"""
# You are a geographic data analyst. Answer based ONLY on this data:
#
# {geo_summary}
#
# Question: {user_question}
#
# Answer concisely. If unsure, say: "I don't know based on the provided data."
# """
#     answer = ask_local_llm(prompt, model="mistral")
#     return JSONResponse(content={"answer": answer})


# import json
# import re
# from typing import Dict, Any, List, Optional
#
# import requests
# from fastapi import FastAPI
# from fastapi.responses import HTMLResponse, JSONResponse
# from pydantic import BaseModel
#
# # Load GeoJSON once at startup
# try:
#     with open("data1.geojson", "r", encoding='utf-8') as f:
#         geojson_data = json.load(f)
#     print(f"✅ GeoJSON loaded successfully. Type: {geojson_data.get('type', 'Unknown')}")
# except Exception as e:
#     print(f"❌ Error loading GeoJSON: {e}")
#     geojson_data = {"type": "FeatureCollection", "features": []}
#
# app = FastAPI(title="GeoJSON AI Agent")
#
#
# class QuestionRequest(BaseModel):
#     question: str
#
#
# HTML_TEMPLATE = """
# <!doctype html>
# <html>
# <head>
#     <title>GeoJSON AI Agent</title>
#     <meta charset="utf-8">
#     <style>
#         body { font-family: Arial, sans-serif; margin: 40px; }
#         input[type="text"] { width: 400px; padding: 8px; }
#         button { padding: 8px 16px; margin-left: 10px; }
#         #answer { margin-top: 20px; padding: 15px; background: #f0f8ff; border-radius: 5px; border: 1px solid #ccc; }
#         .error { background: #ffe6e6 !important; color: #cc0000; }
#         .success { background: #e6ffe6 !important; }
#         ul { max-height: 300px; overflow-y: auto; }
#     </style>
# </head>
# <body>
#     <h2>🔍 Ask about your GeoJSON Data</h2>
#     <form id="questionForm">
#         <input type="text" id="question" name="question"
#                placeholder="e.g., What properties are available? How many features? List all names?"
#                required>
#         <button type="submit">Ask</button>
#     </form>
#     <div id="answer"></div>
#
#     <script>
#         document.getElementById('questionForm').onsubmit = async (e) => {
#             e.preventDefault();
#             const question = document.getElementById('question').value;
#             const answerDiv = document.getElementById('answer');
#             answerDiv.innerHTML = "🤔 Thinking...";
#             answerDiv.className = '';
#
#             try {
#                 const response = await fetch('/ask', {
#                     method: 'POST',
#                     headers: {'Content-Type': 'application/json'},
#                     body: JSON.stringify({question: question})
#                 });
#                 const data = await response.json();
#
#                 if (data.values) {
#                     answerDiv.innerHTML = `
#                         <strong>✅ ${data.answer}</strong>
#                         <ul>${data.values.map(v => `<li>${v}</li>`).join('')}</ul>
#                     `;
#                     answerDiv.className = 'success';
#                 } else if (data.answer) {
#                     answerDiv.innerHTML = data.answer;
#                     answerDiv.className = data.answer.includes('Error') ? 'error' : 'success';
#                 }
#             } catch (error) {
#                 answerDiv.innerHTML = `❌ Error: ${error.message}`;
#                 answerDiv.className = 'error';
#             }
#         };
#     </script>
# </body>
# </html>
# """
#
#
# def ask_local_llm(prompt: str, model: str = "mistral") -> str:
#     """Send prompt to Ollama running on localhost"""
#     url = "http://localhost:11434/api/generate"
#     payload = {
#         "model": model,
#         "prompt": prompt,
#         "stream": False,
#         "options": {"temperature": 0.1}  # Lower temperature for more consistent answers
#     }
#     try:
#         response = requests.post(url, json=payload, timeout=120)
#         if response.status_code == 200:
#             return response.json().get("response", "No response received")
#         else:
#             return f"Error: HTTP {response.status_code} - {response.text}"
#     except Exception as e:
#         return f"Failed to connect to Ollama: {str(e)}"
#
#
# def analyze_geojson_structure(geojson: Dict[str, Any]) -> Dict[str, Any]:
#     """Comprehensive analysis of GeoJSON structure"""
#     analysis = {
#         "type": geojson.get("type", "Unknown"),
#         "total_features": 0,
#         "properties_analysis": {},
#         "geometry_types": set(),
#         "sample_features": [],
#         "crs": geojson.get("crs", {}),
#         "bbox": geojson.get("bbox", [])
#     }
#
#     features = geojson.get("features", [])
#     analysis["total_features"] = len(features)
#
#     if not features:
#         return analysis
#
#     # Analyze first 5 features in detail
#     for i, feature in enumerate(features[:5]):
#         feature_analysis = {
#             "feature_index": i,
#             "type": feature.get("type"),
#             "properties": feature.get("properties", {}),
#             "geometry_type": feature.get("geometry", {}).get("type") if feature.get("geometry") else None
#         }
#         analysis["sample_features"].append(feature_analysis)
#
#         # Collect geometry types
#         if feature_analysis["geometry_type"]:
#             analysis["geometry_types"].add(feature_analysis["geometry_type"])
#
#         # Analyze properties
#         for prop_name, prop_value in feature_analysis["properties"].items():
#             if prop_name not in analysis["properties_analysis"]:
#                 analysis["properties_analysis"][prop_name] = {
#                     "type": type(prop_value).__name__,
#                     "sample_values": set(),
#                     "count": 0
#                 }
#             analysis["properties_analysis"][prop_name]["sample_values"].add(str(prop_value))
#             analysis["properties_analysis"][prop_name]["count"] += 1
#
#     # Convert sets to lists for JSON serialization
#     analysis["geometry_types"] = list(analysis["geometry_types"])
#     for prop in analysis["properties_analysis"]:
#         analysis["properties_analysis"][prop]["sample_values"] = list(
#             analysis["properties_analysis"][prop]["sample_values"]
#         )[:10]  # Limit to 10 sample values
#
#     return analysis
#
#
# def create_geojson_summary(geojson: Dict[str, Any]) -> str:
#     """Create a detailed, structured summary of the GeoJSON for the LLM"""
#     analysis = analyze_geojson_structure(geojson)
#
#     summary_parts = []
#
#     # Basic info
#     summary_parts.append(f"📊 GEOJSON SUMMARY")
#     summary_parts.append(f"Type: {analysis['type']}")
#     summary_parts.append(f"Total Features: {analysis['total_features']}")
#
#     if analysis['bbox']:
#         summary_parts.append(f"Bounding Box: {analysis['bbox']}")
#
#     if analysis['crs']:
#         summary_parts.append(f"Coordinate Reference System: {analysis['crs']}")
#
#     # Geometry types
#     if analysis['geometry_types']:
#         summary_parts.append(f"Geometry Types: {', '.join(analysis['geometry_types'])}")
#
#     # Properties analysis
#     if analysis['properties_analysis']:
#         summary_parts.append("\n📋 PROPERTIES ANALYSIS:")
#         for prop_name, prop_info in analysis['properties_analysis'].items():
#             summary_parts.append(f"  • {prop_name}:")
#             summary_parts.append(f"    - Type: {prop_info['type']}")
#             summary_parts.append(f"    - Count: {prop_info['count']} features")
#             if prop_info['sample_values']:
#                 samples = ', '.join(prop_info['sample_values'][:5])
#                 summary_parts.append(f"    - Sample values: {samples}")
#                 if len(prop_info['sample_values']) > 5:
#                     summary_parts.append(f"    - ... and {len(prop_info['sample_values']) - 5} more unique values")
#
#     # Sample features
#     if analysis['sample_features']:
#         summary_parts.append(f"\n🔍 SAMPLE FEATURES (first {len(analysis['sample_features'])}):")
#         for sample in analysis['sample_features']:
#             summary_parts.append(f"  Feature {sample['feature_index'] + 1}:")
#             summary_parts.append(f"    - Type: {sample['type']}")
#             summary_parts.append(f"    - Geometry: {sample['geometry_type']}")
#             if sample['properties']:
#                 summary_parts.append(f"    - Properties: {sample['properties']}")
#
#     return "\n".join(summary_parts)
#
#
# def extract_property_values(geojson: Dict[str, Any], property_name: str) -> List[str]:
#     """Extract all unique values for a specific property"""
#     values = set()
#     for feature in geojson.get("features", []):
#         prop_value = feature.get("properties", {}).get(property_name)
#         if prop_value is not None:
#             values.add(str(prop_value))
#     return sorted(list(values))
#
#
# def get_feature_count_by_property(geojson: Dict[str, Any], property_name: str) -> Dict[str, int]:
#     """Count features by property value"""
#     counts = {}
#     for feature in geojson.get("features", []):
#         prop_value = feature.get("properties", {}).get(property_name)
#         if prop_value is not None:
#             key = str(prop_value)
#             counts[key] = counts.get(key, 0) + 1
#     return counts
#
#
# @app.get("/", response_class=HTMLResponse)
# async def home():
#     return HTMLResponse(content=HTML_TEMPLATE)
#
#
# @app.post("/ask")
# async def ask(request: QuestionRequest):
#     user_question = request.question.strip().lower()
#
#     print(f"📥 Question: {user_question}")
#
#     # 🎯 Pattern 1: List all values of a specific property
#     list_patterns = [
#         r"list\s+(?:all\s+)?['\"]?(\w+)['\"]?(?:\s+values?)?",
#         r"what\s+are\s+the\s+['\"]?(\w+)['\"]?(?:\s+values?)?",
#         r"show\s+me\s+(?:all\s+)?['\"]?(\w+)['\"]?(?:\s+values?)?",
#         r"get\s+(?:all\s+)?['\"]?(\w+)['\"]?(?:\s+values?)?",
#         r"all\s+['\"]?(\w+)['\"]?(?:\s+values?)?"
#     ]
#
#     property_name = None
#     for pattern in list_patterns:
#         match = re.search(pattern, user_question, re.IGNORECASE)
#         if match:
#             property_name = match.group(1)
#             break
#
#     if property_name:
#         values = extract_property_values(geojson_data, property_name)
#         if values:
#             return JSONResponse(content={
#                 "answer": f"Found {len(values)} unique values for property '{property_name}':",
#                 "values": values
#             })
#         else:
#             return JSONResponse(content={
#                 "answer": f"❌ No values found for property '{property_name}'. Available properties: {list(analyze_geojson_structure(geojson_data)['properties_analysis'].keys())}"
#             })
#
#     # 🎯 Pattern 2: Count features by property value
#     count_pattern = r"how\s+many\s+(?:features?)?\s+(?:have|with)\s+['\"]?(\w+)['\"]?\s*=\s*['\"]?([^'\"]+)['\"]?"
#     match = re.search(count_pattern, user_question, re.IGNORECASE)
#     if match:
#         prop_name, prop_value = match.groups()
#         count = 0
#         for feature in geojson_data.get("features", []):
#             if str(feature.get("properties", {}).get(prop_name, "")).lower() == prop_value.lower():
#                 count += 1
#         return JSONResponse(content={
#             "answer": f"Found {count} features with {prop_name} = '{prop_value}'"
#         })
#
#     # 🎯 Pattern 3: Basic statistics questions
#     if "how many" in user_question and "feature" in user_question:
#         count = len(geojson_data.get("features", []))
#         return JSONResponse(content={
#             "answer": f"📊 Total features: {count}"
#         })
#
#     if "what properties" in user_question or "available properties" in user_question:
#         properties = list(analyze_geojson_structure(geojson_data)["properties_analysis"].keys())
#         if properties:
#             return JSONResponse(content={
#                 "answer": f"📋 Available properties: {', '.join(properties)}",
#                 "values": properties
#             })
#         else:
#             return JSONResponse(content={
#                 "answer": "❌ No properties found in the GeoJSON features"
#             })
#
#     # 🧠 Pattern 4: Use LLM for complex questions
#     geo_summary = create_geojson_summary(geojson_data)
#
#     prompt = f"""
# You are a precise geographic data analyst. Answer based ONLY on this GeoJSON data summary:
#
# {geo_summary}
#
# User Question: {user_question}
#
# Instructions:
# 1. Be factual and concise
# 2. Only use information from the provided summary
# 3. If the answer requires data not in the summary, say: "I cannot answer that with the available data"
# 4. For property names, use exact names from the properties analysis
# 5. Format numbers and lists clearly
#
# Answer:
# """
#
#     answer = ask_local_llm(prompt)
#     return JSONResponse(content={"answer": answer})
#
#
# @app.get("/geojson-info")
# async def geojson_info():
#     """Endpoint to check GeoJSON structure"""
#     analysis = analyze_geojson_structure(geojson_data)
#     return JSONResponse(content=analysis)
#
#
# if __name__ == "__main__":
#     import uvicorn
#
#     print("🚀 Starting GeoJSON AI Agent...")
#     print(f"📁 GeoJSON loaded: {len(geojson_data.get('features', []))} features")
#     uvicorn.run(app, host="0.0.0.0", port=8000)

import json
import re
from typing import Dict, Any, List, Optional
from collections import Counter, defaultdict

import requests
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

# Load GeoJSON once at startup
try:
    with open("data1.geojson", "r", encoding='utf-8') as f:
        geojson_data = json.load(f)
    print(f"✅ GeoJSON loaded successfully. Type: {geojson_data.get('type', 'Unknown')}")
    print(f"📊 Total features: {len(geojson_data.get('features', []))}")
except Exception as e:
    print(f"❌ Error loading GeoJSON: {e}")
    geojson_data = {"type": "FeatureCollection", "features": []}

app = FastAPI(title="GeoJSON AI Agent - Full Data")


class QuestionRequest(BaseModel):
    question: str


HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>GeoJSON AI Agent - Full Data Analysis</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        input[type="text"] { width: 500px; padding: 8px; }
        button { padding: 8px 16px; margin-left: 10px; }
        #answer { margin-top: 20px; padding: 15px; background: #f0f8ff; border-radius: 5px; border: 1px solid #ccc; white-space: pre-wrap; }
        .error { background: #ffe6e6 !important; color: #cc0000; }
        .success { background: #e6ffe6 !important; }
        .info { background: #e6f3ff !important; }
        ul { max-height: 400px; overflow-y: auto; }
        .stats { background: #fff4e6; padding: 10px; border-radius: 5px; margin: 10px 0; }
    </style>
</head>
<body>
    <h2>🔍 GeoJSON Full Data Analysis</h2>
    <div class="stats">
        <strong>📊 Loaded Data:</strong> {{feature_count}} features, {{property_count}} properties
    </div>
    <form id="questionForm">
        <input type="text" id="question" name="question" 
               placeholder="e.g., List all names, What's the most common type?, Statistics for population..." 
               required>
        <button type="submit">Ask</button>
    </form>
    <div id="answer" class="info">Ask a question about the GeoJSON data. I've analyzed all {{feature_count}} features.</div>

    <script>
        document.getElementById('questionForm').onsubmit = async (e) => {
            e.preventDefault();
            const question = document.getElementById('question').value;
            const answerDiv = document.getElementById('answer');
            answerDiv.innerHTML = "🤔 Analyzing all features...";
            answerDiv.className = 'info';

            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({question: question})
                });
                const data = await response.json();

                if (data.values) {
                    const listHtml = data.values.length > 50 ? 
                        `<strong>✅ ${data.answer}</strong><br>
                         <small>Showing first 50 of ${data.values.length} items:</small>
                         <ul>${data.values.slice(0, 50).map(v => `<li>${v}</li>`).join('')}</ul>
                         ${data.values.length > 50 ? `<small>... and ${data.values.length - 50} more</small>` : ''}` :
                        `<strong>✅ ${data.answer}</strong>
                         <ul>${data.values.map(v => `<li>${v}</li>`).join('')}</ul>`;

                    answerDiv.innerHTML = listHtml;
                    answerDiv.className = 'success';
                } else if (data.answer) {
                    answerDiv.innerHTML = data.answer;
                    answerDiv.className = data.answer.includes('❌') ? 'error' : 
                                         data.answer.includes('✅') ? 'success' : 'info';
                }
            } catch (error) {
                answerDiv.innerHTML = `❌ Error: ${error.message}`;
                answerDiv.className = 'error';
            }
        };
    </script>
</body>
</html>
"""


def ask_local_llm(prompt: str, model: str = "mistral") -> str:
    """Send prompt to Ollama running on localhost"""
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1}
    }
    try:
        response = requests.post(url, json=payload, timeout=120)
        if response.status_code == 200:
            return response.json().get("response", "No response received")
        else:
            return f"Error: HTTP {response.status_code}"
    except Exception as e:
        return f"Failed to connect to Ollama: {str(e)}"


def safe_get(obj, *keys, default=None):
    """Safely get nested dictionary values"""
    try:
        for key in keys:
            if isinstance(obj, dict):
                obj = obj.get(key, default)
            else:
                return default
        return obj
    except (AttributeError, TypeError, KeyError):
        return default


def analyze_complete_geojson(geojson: Dict[str, Any]) -> Dict[str, Any]:
    """Comprehensive analysis of ALL features in the GeoJSON with error handling"""
    features = safe_get(geojson, "features", default=[])
    total_features = len(features)

    analysis = {
        "type": safe_get(geojson, "type", default="Unknown"),
        "total_features": total_features,
        "properties_analysis": {},
        "geometry_types": Counter(),
        "crs": safe_get(geojson, "crs", default={}),
        "bbox": safe_get(geojson, "bbox", default=[]),
        "feature_ids": [],
        "features_without_geometry": 0,
        "features_without_properties": 0,
        "malformed_features": 0
    }

    if not features:
        return analysis

    # Analyze ALL features with robust error handling
    for i, feature in enumerate(features):
        try:
            # Skip if feature is not a dictionary
            if not isinstance(feature, dict):
                analysis["malformed_features"] += 1
                continue

            # Track feature IDs safely
            feature_id = safe_get(feature, "id", default=f"feature_{i}")
            analysis["feature_ids"].append(str(feature_id))

            # Analyze geometry safely
            geometry = safe_get(feature, "geometry")
            if geometry and isinstance(geometry, dict):
                geometry_type = safe_get(geometry, "type")
                if geometry_type:
                    analysis["geometry_types"][geometry_type] += 1
            else:
                analysis["features_without_geometry"] += 1

            # Analyze properties safely
            properties = safe_get(feature, "properties", default={})
            if not properties or not isinstance(properties, dict):
                analysis["features_without_properties"] += 1
                continue

            for prop_name, prop_value in properties.items():
                if not isinstance(prop_name, str):
                    continue

                if prop_name not in analysis["properties_analysis"]:
                    analysis["properties_analysis"][prop_name] = {
                        "type": type(prop_value).__name__ if prop_value is not None else "NoneType",
                        "unique_values": set(),
                        "total_count": 0,
                        "null_count": 0,
                        "sample_values": []
                    }

                prop_analysis = analysis["properties_analysis"][prop_name]
                prop_analysis["total_count"] += 1

                if prop_value is None:
                    prop_analysis["null_count"] += 1
                else:
                    try:
                        str_value = str(prop_value)
                        prop_analysis["unique_values"].add(str_value)
                        # Keep last 5 unique sample values
                        if str_value not in prop_analysis["sample_values"]:
                            prop_analysis["sample_values"].append(str_value)
                            if len(prop_analysis["sample_values"]) > 5:
                                prop_analysis["sample_values"].pop(0)
                    except Exception:
                        # Handle cases where prop_value can't be converted to string
                        prop_analysis["unique_values"].add("[unstringable_value]")

        except Exception as e:
            analysis["malformed_features"] += 1
            print(f"⚠️ Error analyzing feature {i}: {e}")
            continue

    # Convert sets to lists and calculate statistics
    for prop_name, prop_info in analysis["properties_analysis"].items():
        prop_info["unique_values"] = list(prop_info["unique_values"])
        prop_info["unique_count"] = len(prop_info["unique_values"])
        prop_info["coverage_percent"] = (prop_info["total_count"] / total_features) * 100 if total_features > 0 else 0

        # Calculate value frequencies for top values
        if prop_info["unique_count"] <= 20:  # Only for properties with limited unique values
            value_counts = Counter()
            for feature in features:
                if isinstance(feature, dict):
                    value = safe_get(feature, "properties", prop_name)
                    if value is not None:
                        try:
                            value_counts[str(value)] += 1
                        except Exception:
                            value_counts["[unstringable_value]"] += 1
            prop_info["value_frequencies"] = dict(value_counts.most_common(10))

    # Convert Counter to dict
    analysis["geometry_types"] = dict(analysis["geometry_types"])

    print(f"✅ Analysis complete: {total_features} features, {len(analysis['properties_analysis'])} properties")
    print(
        f"⚠️  Issues: {analysis['malformed_features']} malformed, {analysis['features_without_geometry']} no geometry, {analysis['features_without_properties']} no properties")

    return analysis


def create_complete_geojson_summary(geojson: Dict[str, Any]) -> str:
    """Create a detailed summary analyzing ALL features"""
    analysis = analyze_complete_geojson(geojson)

    summary_parts = []

    # Basic info
    summary_parts.append("📊 COMPLETE GEOJSON ANALYSIS (ALL FEATURES)")
    summary_parts.append("=" * 50)
    summary_parts.append(f"Type: {analysis['type']}")
    summary_parts.append(f"Total Features: {analysis['total_features']:,}")

    # Report any issues
    if analysis['malformed_features'] > 0:
        summary_parts.append(f"⚠️  Malformed Features: {analysis['malformed_features']:,}")
    if analysis['features_without_geometry'] > 0:
        summary_parts.append(f"⚠️  Features without geometry: {analysis['features_without_geometry']:,}")
    if analysis['features_without_properties'] > 0:
        summary_parts.append(f"⚠️  Features without properties: {analysis['features_without_properties']:,}")

    if analysis['bbox']:
        summary_parts.append(f"Bounding Box: {analysis['bbox']}")

    # Geometry types
    if analysis['geometry_types']:
        summary_parts.append(f"\n📍 GEOMETRY TYPES:")
        for geom_type, count in analysis['geometry_types'].items():
            percentage = (count / analysis['total_features']) * 100
            summary_parts.append(f"  • {geom_type}: {count:,} features ({percentage:.1f}%)")

    # Properties analysis - ALL properties from ALL features
    if analysis['properties_analysis']:
        summary_parts.append(f"\n📋 PROPERTIES ANALYSIS (from all {analysis['total_features']:,} features):")
        for prop_name, prop_info in analysis['properties_analysis'].items():
            summary_parts.append(f"  🏷️  {prop_name}:")
            summary_parts.append(f"     - Data Type: {prop_info['type']}")
            summary_parts.append(
                f"     - Coverage: {prop_info['total_count']:,}/{analysis['total_features']:,} features ({prop_info['coverage_percent']:.1f}%)")
            summary_parts.append(f"     - Unique Values: {prop_info['unique_count']:,}")
            summary_parts.append(f"     - Null Values: {prop_info['null_count']:,}")

            if prop_info['sample_values']:
                samples = ', '.join(prop_info['sample_values'])
                summary_parts.append(f"     - Sample Values: {samples}")

            # Show value frequencies for properties with limited unique values
            if 'value_frequencies' in prop_info and prop_info['value_frequencies']:
                summary_parts.append(f"     - Value Distribution:")
                for value, count in list(prop_info['value_frequencies'].items())[:5]:
                    percentage = (count / prop_info['total_count']) * 100
                    summary_parts.append(f"       • '{value}': {count:,} ({percentage:.1f}%)")

    # Feature ID sample
    if analysis['feature_ids']:
        summary_parts.append(f"\n🔍 FEATURE ID SAMPLE (first 10):")
        summary_parts.append(f"  {', '.join(analysis['feature_ids'][:10])}")
        if len(analysis['feature_ids']) > 10:
            summary_parts.append(f"  ... and {len(analysis['feature_ids']) - 10:,} more")

    return "\n".join(summary_parts)


def extract_all_property_values(geojson: Dict[str, Any], property_name: str, limit: int = 1000) -> List[str]:
    """Extract ALL values for a specific property from ALL features safely"""
    values = []
    features = safe_get(geojson, "features", default=[])

    for feature in features:
        if not isinstance(feature, dict):
            continue

        prop_value = safe_get(feature, "properties", property_name)
        if prop_value is not None:
            try:
                values.append(str(prop_value))
            except Exception:
                values.append("[unstringable_value]")

        if len(values) >= limit:  # Safety limit
            break

    return values


def extract_unique_property_values(geojson: Dict[str, Any], property_name: str) -> List[str]:
    """Extract ALL UNIQUE values for a specific property safely"""
    unique_values = set()
    features = safe_get(geojson, "features", default=[])

    for feature in features:
        if not isinstance(feature, dict):
            continue

        prop_value = safe_get(feature, "properties", property_name)
        if prop_value is not None:
            try:
                unique_values.add(str(prop_value))
            except Exception:
                unique_values.add("[unstringable_value]")

    return sorted(list(unique_values))


def get_property_statistics(geojson: Dict[str, Any], property_name: str) -> Dict[str, Any]:
    """Get comprehensive statistics for a property safely"""
    values = []
    numeric_values = []
    features = safe_get(geojson, "features", default=[])

    for feature in features:
        if not isinstance(feature, dict):
            continue

        prop_value = safe_get(feature, "properties", property_name)
        if prop_value is not None:
            values.append(prop_value)
            # Try to convert to numeric for statistics
            try:
                if isinstance(prop_value, (int, float)):
                    numeric_values.append(prop_value)
                else:
                    numeric_val = float(prop_value)
                    numeric_values.append(numeric_val)
            except (ValueError, TypeError):
                pass

    stats = {
        "total_count": len(values),
        "unique_count": len(set(str(v) for v in values)),
        "value_types": Counter(type(v).__name__ for v in values),
        "top_values": Counter(str(v) for v in values).most_common(10)
    }

    if numeric_values:
        stats["numeric"] = {
            "min": min(numeric_values),
            "max": max(numeric_values),
            "mean": sum(numeric_values) / len(numeric_values),
            "count": len(numeric_values)
        }

    return stats


@app.get("/", response_class=HTMLResponse)
async def home():
    analysis = analyze_complete_geojson(geojson_data)
    feature_count = analysis['total_features']
    property_count = len(analysis['properties_analysis'])

    html_content = HTML_TEMPLATE.replace("{{feature_count}}", f"{feature_count:,}") \
        .replace("{{property_count}}", str(property_count))
    return HTMLResponse(content=html_content)


@app.post("/ask")
async def ask(request: QuestionRequest):
    user_question = request.question.strip().lower()

    print(f"📥 Question: {user_question}")
    print(f"📊 Analyzing all {len(geojson_data.get('features', []))} features...")

    # Get complete analysis
    complete_analysis = analyze_complete_geojson(geojson_data)

    # 🎯 Pattern 1: List all values of a specific property
    list_patterns = [
        r"list\s+(?:all\s+)?['\"]?(\w+)['\"]?(?:\s+values?)?",
        r"what\s+are\s+the\s+['\"]?(\w+)['\"]?(?:\s+values?)?",
        r"show\s+me\s+(?:all\s+)?['\"]?(\w+)['\"]?(?:\s+values?)?",
        r"get\s+(?:all\s+)?['\"]?(\w+)['\"]?(?:\s+values?)?",
        r"all\s+['\"]?(\w+)['\"]?(?:\s+values?)?",
        r"unique\s+['\"]?(\w+)['\"]?(?:\s+values?)?"
    ]

    property_name = None
    for pattern in list_patterns:
        match = re.search(pattern, user_question, re.IGNORECASE)
        if match:
            property_name = match.group(1)
            break

    if property_name:
        if property_name in complete_analysis["properties_analysis"]:
            unique_values = extract_unique_property_values(geojson_data, property_name)
            all_values = extract_all_property_values(geojson_data, property_name, limit=1000)

            prop_info = complete_analysis["properties_analysis"][property_name]

            if "unique" in user_question:
                return JSONResponse(content={
                    "answer": f"✅ Found {len(unique_values):,} unique values for '{property_name}' (from {prop_info['total_count']:,} features):",
                    "values": unique_values
                })
            else:
                return JSONResponse(content={
                    "answer": f"✅ Found {prop_info['total_count']:,} values for '{property_name}' ({len(unique_values):,} unique). Showing first {len(all_values):,}:",
                    "values": all_values
                })
        else:
            available_props = list(complete_analysis["properties_analysis"].keys())
            return JSONResponse(content={
                "answer": f"❌ Property '{property_name}' not found. Available properties: {', '.join(available_props)}"
            })

    # 🎯 Pattern 2: Statistics for a property
    stats_pattern = r"(?:statistics|stats|analysis|describe)\s+(?:for|of)\s+['\"]?(\w+)['\"]?"
    match = re.search(stats_pattern, user_question, re.IGNORECASE)
    if match:
        property_name = match.group(1)
        if property_name in complete_analysis["properties_analysis"]:
            stats = get_property_statistics(geojson_data, property_name)
            prop_info = complete_analysis["properties_analysis"][property_name]

            response_lines = [
                f"📊 Statistics for '{property_name}':",
                f"• Total values: {stats['total_count']:,}",
                f"• Unique values: {stats['unique_count']:,}",
                f"• Coverage: {prop_info['coverage_percent']:.1f}% of features",
                f"• Data types: {dict(stats['value_types'])}"
            ]

            if stats['top_values']:
                response_lines.append("• Most common values:")
                for value, count in stats['top_values'][:5]:
                    percentage = (count / stats['total_count']) * 100
                    response_lines.append(f"  - '{value}': {count:,} ({percentage:.1f}%)")

            if 'numeric' in stats:
                num_stats = stats['numeric']
                response_lines.extend([
                    f"• Numeric statistics ({num_stats['count']:,} numeric values):",
                    f"  - Min: {num_stats['min']}",
                    f"  - Max: {num_stats['max']}",
                    f"  - Mean: {num_stats['mean']:.2f}"
                ])

            return JSONResponse(content={"answer": "\n".join(response_lines)})

    # 🎯 Pattern 3: Basic questions
    if "how many features" in user_question:
        count = complete_analysis["total_features"]
        return JSONResponse(content={
            "answer": f"📊 Total features: {count:,}"
        })

    if "what properties" in user_question or "available properties" in user_question:
        properties = list(complete_analysis["properties_analysis"].keys())
        property_info = []
        for prop in properties:
            info = complete_analysis["properties_analysis"][prop]
            property_info.append(f"{prop} ({info['total_count']:,} features, {info['unique_count']:,} unique values)")

        return JSONResponse(content={
            "answer": f"📋 Available properties (from all {complete_analysis['total_features']:,} features):\n" + "\n".join(
                property_info),
            "values": properties
        })

    if "most common" in user_question or "most frequent" in user_question:
        # Find property mentioned in question
        for prop_name in complete_analysis["properties_analysis"]:
            if prop_name in user_question:
                stats = get_property_statistics(geojson_data, prop_name)
                if stats['top_values']:
                    top_value, top_count = stats['top_values'][0]
                    percentage = (top_count / stats['total_count']) * 100
                    return JSONResponse(content={
                        "answer": f"🎯 Most common value for '{prop_name}': '{top_value}' with {top_count:,} occurrences ({percentage:.1f}% of {stats['total_count']:,} values)"
                    })

    # 🧠 Pattern 4: Use LLM for complex questions with COMPLETE data
    complete_summary = create_complete_geojson_summary(geojson_data)

    prompt = f"""
You are a precise geographic data analyst. Answer based ONLY on this COMPLETE GeoJSON analysis of ALL features:

{complete_summary}

User Question: {user_question}

Instructions:
1. Be factual and concise
2. Use the complete dataset analysis (all {complete_analysis['total_features']:,} features)
3. Reference specific statistics from the analysis
4. If the answer requires data not in the summary, say: "I cannot answer that with the available data"
5. Format numbers with commas for thousands

Answer:
"""

    answer = ask_local_llm(prompt)
    return JSONResponse(content={"answer": answer})


@app.get("/geojson-info")
async def geojson_info():
    """Endpoint to check complete GeoJSON structure"""
    analysis = analyze_complete_geojson(geojson_data)
    return JSONResponse(content=analysis)


@app.get("/property/{property_name}")
async def get_property_values(property_name: str, unique: bool = False, limit: int = 100):
    """Direct API endpoint to get property values"""
    if unique:
        values = extract_unique_property_values(geojson_data, property_name)
    else:
        values = extract_all_property_values(geojson_data, property_name, limit=limit)

    return JSONResponse(content={
        "property": property_name,
        "values": values,
        "count": len(values),
        "unique": unique
    })


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting GeoJSON AI Agent with COMPLETE data analysis...")
    feature_count = len(geojson_data.get('features', []))
    print(f"📁 GeoJSON loaded: {feature_count:,} features")

    # Pre-analyze the complete dataset
    analysis = analyze_complete_geojson(geojson_data)
    print(f"📊 Properties found: {list(analysis['properties_analysis'].keys())}")

    uvicorn.run(app, host="0.0.0.0", port=8000)