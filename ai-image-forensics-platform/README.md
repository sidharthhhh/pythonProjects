# AI Image Authenticity & Forensics Platform

A production-grade platform for detecting AI-generated images through a multi-layer forensic pipeline:

- 🛡️ **C2PA Provenance** — Cryptographic manifest verification
- 💦 **Invisible Watermark Detection** — SynthID / Stable Diffusion pattern matching
- 🧠 **Statistical ML Classifier** — Edge density, entropy, color uniformity analysis
- 📊 **Metadata Analysis** — EXIF/XMP AI generator tag detection
- 🔬 **Forensic Analysis** — Error Level Analysis (ELA) + Fourier Spectrum
- 🌀 **Diffusion Noise Fingerprinting** — Non-local means denoising residual analysis

---

## 🏗️ Project Structure

```
ai-image-forensics-platform/
├── app/
│   ├── main.py                  # FastAPI application entry
│   ├── api/routes/upload.py     # POST /api/v1/analyze endpoint
│   ├── core/
│   │   ├── config.py            # Pydantic settings
│   │   └── security.py          # File validation & auth
│   ├── detectors/
│   │   ├── metadata.py          # EXIF/XMP analysis
│   │   ├── c2pa_verifier.py     # C2PA manifest checker
│   │   ├── watermark.py         # Invisible watermark detector
│   │   ├── ai_classifier.py     # Statistical ML classifier
│   │   ├── forensic.py          # ELA + Fourier + noise analysis
│   │   ├── diffusion.py         # Diffusion noise fingerprinting
│   │   └── manipulation.py      # Recompression detection
│   ├── engine/
│   │   └── decision.py          # Weighted scoring & explainability
│   ├── models/
│   │   └── schemas.py           # Pydantic response models
│   └── pipeline/
│       └── orchestrator.py      # Async parallel detector executor
├── frontend/
│   ├── index.html               # Web UI
│   ├── styles.css               # Glassmorphism styling
│   └── app.js                   # API integration
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## 🚀 Running the Project

### Option 1: With Docker (Recommended)

**Prerequisites:** Docker & Docker Compose installed

```bash
# 1. Clone the repository
git clone https://github.com/sidharthhhh/pythonProjects.git
cd pythonProjects/ai-image-forensics-platform

# 2. Build and start all containers (API + Redis + Celery Worker)
docker-compose up --build -d

# 3. Verify the API is running
curl http://localhost:8000/health
# Expected: {"status":"healthy","version":"1.0.0"}

# 4. Start the frontend (in a separate terminal)
cd frontend
python -m http.server 3000

# 5. Open in browser
# API Docs:  http://localhost:8000/docs
# Web UI:    http://localhost:3000
```

**Useful Docker Commands:**
```bash
# View live API logs
docker-compose logs -f api

# Restart just the API container
docker-compose restart api

# Stop all containers
docker-compose down

# Rebuild from scratch (after code changes)
docker-compose up --build -d
```

---

### Option 2: Without Docker (Local Development)

**Prerequisites:** Python 3.10+, Redis server running locally

```bash
# 1. Clone the repository
git clone https://github.com/sidharthhhh/pythonProjects.git
cd pythonProjects/ai-image-forensics-platform

# 2. Create and activate a virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start Redis (required for Celery task queue)
# On Windows (via WSL or Docker):
redis-server
# On macOS:
brew services start redis

# 5. Set environment variables
# On Windows (PowerShell):
$env:REDIS_URL="redis://localhost:6379/0"
$env:ENVIRONMENT="development"

# On macOS/Linux:
export REDIS_URL="redis://localhost:6379/0"
export ENVIRONMENT="development"

# 6. Start the FastAPI backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 7. Start the frontend (in a separate terminal)
cd frontend
python -m http.server 3000

# 8. Open in browser
# API Docs:  http://localhost:8000/docs
# Web UI:    http://localhost:3000
```

---

## 📡 API Usage

### Analyze an Image

```bash
# Using curl
curl -X POST http://localhost:8000/api/v1/analyze \
  -F "file=@path/to/image.jpg"
```

### Example Response

```json
{
  "ai_generated_probability": 0.82,
  "confidence_score": 0.95,
  "c2pa_verified": false,
  "watermark_detected": false,
  "metadata_ai_hint": false,
  "forensic_signals": ["diffusion_synthetic_noise", "ai_texture_anomaly"],
  "explanation": "Image shows strong AI generation signatures from multiple forensic layers."
}
```

### Health Check

```bash
curl http://localhost:8000/health
```

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI + Uvicorn |
| Image Processing | OpenCV, NumPy, SciPy, Pillow |
| Task Queue | Celery + Redis |
| Containerization | Docker + Docker Compose |
| Observability | Prometheus + OpenTelemetry |

---

## 📄 License

MIT License
