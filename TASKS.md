
# ✅ Spatia – The Simplest GIS Agent that can handle native GIS Files

## 🧱 Setup Phase
- [ ] Initialize Django project (`frontend`)
- [ ] Create Django app
- [ ] Create FastAPI project (`backend`)
- [ ] Create `run_frontend.sh` and `run_backend.sh` to start servers

## 🎨 Frontend (Django UI)

### Upload & Input Form
- [ ] Add HTML form for GeoJSON upload
- [ ] Add input box for user question
- [ ] Add submit button
- [ ] Use JS (AJAX or Fetch API) to send form data to FastAPI

### Response Display
- [ ] Display LLM response in the same page

## 🚀 Backend (FastAPI)

### File Upload Route (`/upload`)
- [ ] Accept GeoJSON file
- [ ] Validate file content
- [ ] Parse JSON into memory or store temporarily

### Analysis Route (`/analyze`)
- [ ] Accept user prompt + GeoJSON content
- [ ] Parse GeoJSON features
- [ ] Generate spatial metadata (e.g., feature count, bounds, geometry types)
- [ ] Format input prompt for Mistral
- [ ] Send prompt to Mistral local API
- [ ] Return LLM response

## 🧠 Services

### `geojson_utils.py`
- [ ] Parse and validate GeoJSON
- [ ] Extract:
  - Geometry types
  - Centroids or bounding boxes
  - Number of features
  - CRS info (if present)

### `llm_client.py`
- [ ] Connect to local Mistral API or socket
- [ ] Format prompt using metadata + user question
- [ ] Return text response

## 🔁 Integration
- [ ] Connect Django JS to FastAPI backend
- [ ] Handle POST request to `/analyze`
- [ ] Display analysis result dynamically on same page

## 🧪 Testing & QA
- [ ] Test file upload and parsing
- [ ] Test question prompt with valid GeoJSON
- [ ] Handle malformed GeoJSON and invalid questions

## 📦 Optional Enhancements
- [ ] Add Leaflet.js map preview of uploaded GeoJSON
- [ ] Allow user to draw features and export as GeoJSON
- [ ] Add loading spinner while waiting for response
- [ ] Save past queries and responses (session-based)
