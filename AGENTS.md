# FinancePilot AI - Agent Notes

## Project Information

This is a multi-model agentic financial intelligence platform built for a hackathon.

## Build Commands

### Frontend
```bash
npm run dev          # Start Vite dev server on port 5173
npm run build        # Production build
npm run preview      # Preview production build
```

### Backend (Express)
```bash
PORT=3001 ML_SERVICE_URL=http://localhost:8000 node server/index.cjs
```

### ML Service (FastAPI)
```bash
cd ml
source venv/bin/activate
uvicorn api:app --host 0.0.0.0 --port 8000
```

### ML Training
```bash
cd ml
source venv/bin/activate
python train.py
```

## Quick Start

1. Install dependencies:
   - `npm install` (Node.js)
   - `cd ml && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt` (Python)

2. Train ML model:
   - `cd ml && source venv/bin/activate && python train.py`

3. Start all services (3 terminals):
   - Terminal 1: ML service (port 8000)
   - Terminal 2: Express backend (port 3001)
   - Terminal 3: React frontend (port 5173)

4. Or use startup script:
   - macOS/Linux: `./start.sh`
   - Windows: `start.bat`

## Environment Variables

Required in `.env`:
- `GEMINI_API_KEY` (optional - demo mode works without it)
- `PORT=3001`
- `ML_SERVICE_URL=http://localhost:8000`
- `VITE_API_URL=http://localhost:3001`

## Important Notes

- The ML model is trained on the UCI Default of Credit Card Clients dataset (Taiwan 2005)
- Demo mode works without Gemini API key
- All model predictions include explicit limitations
- The system clearly distinguishes between verified data, calculations, ML predictions, and AI interpretations

## Dataset Location

The UCI dataset is downloaded to `data/default_of_credit_card_clients.xls` during training.

## ML Artifacts

All ML artifacts are saved in `ml/artifacts/`:
- `model.joblib` - Trained model pipeline
- `metrics.json` - Evaluation metrics
- `feature_importance.json` - Feature importance scores
- `feature_schema.json` - Feature names and schema
- `demo_sample.json` - Demo sample features
- `demo_label.json` - Demo sample true label
- `metadata.json` - Model metadata and limitations

## Testing

ML API tests:
```bash
cd ml
source venv/bin/activate
python tests/test_api.py
```

## Current Status

All P0 features are implemented and working:
- ✅ React/Vite dashboard
- ✅ Express backend with Gemini integration
- ✅ ML training pipeline with real metrics
- ✅ FastAPI prediction service
- ✅ Multi-agent workflow
- ✅ Demo mode with fallback
- ✅ End-to-end testing completed
