# FinancePilot AI

Multi-Model Agentic Financial Intelligence Platform

FinancePilot AI combines large language models, classical machine learning, deterministic financial calculations, and independent verification to help users understand financial information. The platform distinguishes between verified source data, calculated metrics, ML predictions, AI-generated interpretations, and unverified assumptions.

## Features

- **Multi-Agent Architecture**: Coordinated workflow with specialized agents
  - Financial Research Agent (Gemini-powered analysis)
  - Quantitative Analysis Agent (deterministic financial calculations)
  - ML Risk Agent (Random Forest classifier predictions)
  - Independent Review Agent (claim verification)

- **Machine Learning**: Trained Random Forest model on UCI Default of Credit Card Clients dataset
  - Real evaluation metrics from held-out test set
  - Feature importance visualization
  - Explicit model limitations and caveats

- **Premium Dashboard**: Modern dark-mode React interface
  - Financial snapshot with key ratios
  - ML risk assessment with probability estimates
  - Agent execution status tracking
  - Comprehensive research reports
  - Demo mode for offline testing

- **Responsible AI**: Clear separation of data types
  - Verified source data
  - Calculated financial metrics
  - Machine-learning predictions (with uncertainty)
  - AI-generated interpretations
  - Unverified assumptions

## Architecture

```
financepilot/
├── src/                    # React frontend
│   ├── components/         # UI components
│   ├── App.jsx            # Main application
│   └── main.jsx           # Entry point
├── server/                # Express backend
│   ├── agents/            # Research and review agents
│   ├── services/          # ML client and quantitative analysis
│   └── index.cjs          # API server
├── ml/                    # Python ML backend
│   ├── train.py           # Training pipeline
│   ├── api.py             # FastAPI prediction service
│   ├── artifacts/         # Trained model and metrics
│   └── tests/             # API tests
└── data/                  # Datasets and sample documents
```

## Prerequisites

- Node.js 18+ and npm
- Python 3.8+
- (Optional) Gemini API key for AI research features

## Quick Start

### 1. Install Dependencies

```bash
# Install Node.js dependencies
npm install

# Install Python dependencies
cd ml
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

### 2. Train ML Model

```bash
cd ml
source venv/bin/activate
python train.py
```

This will:
- Download the UCI Default of Credit Card Clients dataset
- Train a Random Forest classifier
- Save model artifacts and evaluation metrics
- Generate a demo sample for testing

### 3. Start Services

Open three terminal windows:

**Terminal 1 - ML Service:**
```bash
cd ml
source venv/bin/activate
uvicorn api:app --host 0.0.0.0 --port 8000
```

**Terminal 2 - Express Backend:**
```bash
# Create .env file (see Configuration section)
PORT=3001 ML_SERVICE_URL=http://localhost:8000 node server/index.cjs
```

**Terminal 3 - React Frontend:**
```bash
npm run dev
```

### 4. Access the Application

Open your browser to: http://localhost:5173

Click "Demo Mode" to see a demonstration with preloaded data, or enter a financial research question and click "Analyze".

## Configuration

Create a `.env` file in the project root (see `.env.example`):

```bash
# Gemini API Key (optional - demo mode works without it)
GEMINI_API_KEY=your_gemini_api_key_here

# Server Configuration
PORT=3001
ML_SERVICE_URL=http://localhost:8000

# React App Configuration
VITE_API_URL=http://localhost:3001
```

### Getting a Gemini API Key

1. Visit https://makersuite.google.com/app/apikey
2. Create a new API key
3. Add it to your `.env` file
4. Restart the Express server

## ML Model Details

### Dataset
- **Source**: UCI Default of Credit Card Clients
- **URL**: https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients
- **License**: CC BY 4.0
- **Description**: Historical Taiwanese credit card client data from 2005
- **Samples**: 30,000 records
- **Target**: Next-month default payment (Yes/No)

### Model
- **Algorithm**: Random Forest Classifier
- **Features**: 19 financial features (demographics excluded)
- **Training/Test Split**: 80/20 stratified split
- **Random Seed**: 42 (reproducible)

### Evaluation Metrics (Held-out Test Set)
- Accuracy: 0.7948
- Precision (default class): 0.5386
- Recall (default class): 0.5041
- F1-score: 0.5208
- ROC-AUC: 0.7500
- Average Precision: 0.5121

### Important Limitations
- Historical Taiwanese dataset from 2005
- Not validated for Indian borrowers
- Not a model of company financial health
- Demographic fields excluded from training but this does not guarantee fairness
- Model probabilities are uncalibrated
- For demonstration and educational purposes only

## API Endpoints

### Express Backend (Port 3001)

- `GET /api/health` - Health check
- `POST /api/analyze` - Full analysis with all agents
- `POST /api/analyze-demo` - Demo mode with preloaded data

### ML Service (Port 8000)

- `GET /health` - Health check
- `GET /metrics` - Model evaluation metrics
- `GET /feature-importance` - Feature importance scores
- `GET /schema` - Feature schema
- `GET /metadata` - Model metadata
- `GET /predict-demo` - Prediction for demo sample
- `POST /predict` - Prediction for custom features

## Demo Mode

Demo mode works without:
- Gemini API key
- Live market data
- External data sources

It uses:
- Preloaded synthetic financial data
- Trained ML model with real predictions
- Held-out test sample for demonstration
- Real evaluation metrics from training

Demo mode is clearly labeled in the UI and should not be used for actual financial decisions.

## Testing

### ML API Tests
```bash
cd ml
source venv/bin/activate
pip install pytest httpx
python tests/test_api.py
```

### Manual Testing
1. Start all services (see Quick Start)
2. Open http://localhost:5173
3. Click "Demo Mode" to test without Gemini
4. Enter a query and click "Analyze" to test with Gemini (if configured)

## Troubleshooting

### ML Training Fails
- **SSL Certificate Error**: The dataset is downloaded to `data/` automatically. If download fails, download manually from the UCI link and save as `data/default_of_credit_card_clients.xls`
- **Missing Dependencies**: Ensure all Python packages are installed: `pip install -r requirements.txt`

### ML Service Won't Start
- **Model Not Found**: Run `python train.py` first to generate model artifacts
- **Port Conflict**: Change the port in the uvicorn command or ML_SERVICE_URL

### Express Server Won't Start
- **Gemini Not Configured**: This is expected - demo mode works without Gemini
- **ML Service Unreachable**: Ensure ML service is running on port 8000

### Frontend Won't Load
- **Backend Not Running**: Ensure Express server is running on port 3001
- **CORS Errors**: Check that VITE_API_URL matches the backend URL

## Security

- API keys are read from environment variables only
- `.env` file is gitignored
- No credentials are exposed to the React frontend
- Input validation on all API endpoints
- Request size limits enforced
- CORS restricted to localhost for development

## Disclaimer

FinancePilot AI is for research and educational purposes only. It does not provide:
- Personalized investment advice
- Validated credit scoring
- Live trading capabilities
- Automated financial decisions

Before commercial use in India, assess applicable privacy, financial-sector, lending, and securities regulations with qualified professionals.

## Dataset Attribution

Default of Credit Card Clients Dataset
- Source: UCI Machine Learning Repository
- URL: https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients
- License: CC BY 4.0
- Citation: Yeh, I. C., & Lien, C. H. (2009). The comparisons of data mining techniques for the predictive accuracy of probability of default of credit card clients. Expert Systems with Applications, 36(2), 2473-2480.

## Hackathon Presentation

### 90-Second Demo Script

**0-15s**: Introduce the problem of fragmented financial research.

**15-30s**: Show the FinancePilot dashboard and the analysis workflow.

**30-45s**: Show the trained Random Forest model and real held-out evaluation metrics.

**45-60s**: Show the Gemini researcher and independent reviewer examining the available evidence.

**60-75s**: Show a concrete example of an unsupported claim, missing input, or model limitation being surfaced.

**75-90s**: Explain the architecture, the model's limitations, and the next step toward verified real financial data.

## License

This project is for demonstration purposes. The UCI dataset is licensed under CC BY 4.0.

## Next Steps

Future enhancements (P1/P2 priority):
- PostgreSQL persistence
- Second independent model provider
- User authentication
- Advanced retrieval-augmented generation
- Portfolio monitoring
- Additional quantitative models
- Real company data integration
