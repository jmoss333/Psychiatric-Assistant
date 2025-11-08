# ML Engine Integration Guide

Complete guide for integrating the ML Engine with the Express.js backend.

---

## Overview

The ML Engine microservice provides:
1. **Clinical Scenario Classification** - Categorizes patient scenarios
2. **Therapy Modality Recommendations** - Suggests evidence-based treatments
3. **Outcome Predictions** - Estimates treatment success probability

The Express.js backend calls the ML Engine via HTTP REST API.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                       │
└────────────────┬────────────────────────────────────────┘
                 │ HTTP/REST
┌────────────────▼────────────────────────────────────────┐
│          Express.js Backend (Node.js)                    │
│  ├─ Authentication (JWT)                                │
│  ├─ Patient Management                                  │
│  ├─ Clinical Scenario Capture                           │
│  └─ [NEW] ML Integration Layer                          │
└────────────────┬────────────────────────────────────────┘
                 │ HTTP/REST to /recommend
┌────────────────▼────────────────────────────────────────┐
│      ML Engine (FastAPI, Python)                         │
│  ├─ Scenario Classifier (BioBERT)                       │
│  ├─ Modality Recommender (LightGBM)                     │
│  └─ Outcome Predictor (Neural Network)                  │
└────────────────┬────────────────────────────────────────┘
                 │ SQL Queries
┌────────────────▼────────────────────────────────────────┐
│      PostgreSQL Database                                 │
│  ├─ Clinical data                                       │
│  ├─ Therapy modalities                                  │
│  └─ Recommendations history                             │
└─────────────────────────────────────────────────────────┘
```

---

## Step 1: Project Structure

The ML Engine is located at `/ml-engine`:

```
ml-engine/
├── main.py                          # FastAPI application entry point
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment configuration template
├── Dockerfile                       # Docker image for ML engine
│
├── models/
│   ├── __init__.py
│   ├── scenario_classifier.py       # BioBERT-based scenario classification
│   ├── modality_recommender.py      # LightGBM therapy recommendations
│   └── outcome_predictor.py         # Neural network outcome prediction
│
├── utils/
│   ├── __init__.py
│   └── db_connector.py              # PostgreSQL connection management
│
├── scripts/
│   └── extract_training_data.py     # Extract training data from DB
│
├── logs/                            # Application logs
├── models/trained/                  # Trained model binaries
└── data/                            # Training and test data
```

---

## Step 2: Environment Setup

### 2A: Local Development (Non-Docker)

```bash
# 1. Navigate to ML engine directory
cd ml-engine

# 2. Create Python virtual environment
python3 -m venv venv

# 3. Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Copy and configure environment
cp .env.example .env
# Edit .env with your database credentials

# 6. Start ML Engine
python main.py
# Server will start on http://localhost:5000
```

### 2B: Docker Deployment

```bash
# 1. From project root, build and run entire system
docker-compose up

# 2. Services will be available at:
# - PostgreSQL:   localhost:5432
# - Backend:      http://localhost:3000
# - ML Engine:    http://localhost:5000
```

---

## Step 3: Backend Integration

### 3A: Add ML Integration Endpoint (Backend)

Add this to `/backend/routes/recommendations.js`:

```javascript
const express = require('express');
const axios = require('axios');
const { authenticateToken } = require('../middleware/auth');

const router = express.Router();
const ML_ENGINE_URL = process.env.ML_ENGINE_URL || 'http://localhost:5000';

// GET recommendations for a clinical scenario
router.post('/recommendations/scenario', authenticateToken, async (req, res) => {
  try {
    const {
      patient_id,
      scenario_id,
      presenting_problems,
      dsm5_codes,
      symptom_severity,
      assessment_scales,
      psychosocial_stressors,
      protective_factors,
      trauma_history,
      substance_use,
      therapist_notes,
      previous_modalities,
      treatment_goals
    } = req.body;

    // Prepare clinical scenario for ML Engine
    const scenario = {
      patient_id,
      scenario_id,
      presenting_problems,
      dsm5_codes,
      symptom_severity,
      assessment_scales,
      psychosocial_stressors,
      protective_factors,
      trauma_history,
      substance_use,
      therapist_notes,
      previous_modalities,
      treatment_goals
    };

    // Call ML Engine
    const response = await axios.post(
      `${ML_ENGINE_URL}/recommend`,
      scenario,
      { timeout: 30000 }
    );

    // Save recommendations to database
    // TODO: Implement recommendation storage

    res.json({
      success: true,
      recommendations: response.data.recommendations,
      confidence_level: response.data.confidence_level,
      generated_at: response.data.generated_at
    });

  } catch (error) {
    console.error('Error getting recommendations:', error.message);
    res.status(500).json({
      error: 'Failed to generate recommendations',
      message: error.message
    });
  }
});

module.exports = router;
```

### 3B: Register Route in Backend App

In `/backend/app.js`, add:

```javascript
const recommendationsRouter = require('./routes/recommendations');

// ... existing middleware ...

app.use('/api/v1/recommendations', recommendationsRouter);
```

### 3C: Update .env in Backend

Add ML Engine configuration:

```env
# ... existing config ...

# ML Engine Integration
ML_ENGINE_URL=http://localhost:5000
ML_ENGINE_TIMEOUT=30000
```

---

## Step 4: Testing Integration

### 4A: Test ML Engine Health

```bash
# Check ML Engine is running
curl http://localhost:5000/health

# Expected response:
# {
#   "status": "healthy",
#   "models_loaded": true,
#   "database_connected": true
# }
```

### 4B: Test Recommendation Endpoint

```bash
# Get JWT token first (from backend login)
export TOKEN="your_jwt_token_here"

# Call recommendation endpoint
curl -X POST http://localhost:3000/api/v1/recommendations/scenario \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "patient_id": "p123",
    "scenario_id": "s456",
    "presenting_problems": ["anxiety", "depression"],
    "dsm5_codes": ["F41.1", "F32.9"],
    "symptom_severity": {
      "anxiety": 7,
      "depression": 6
    },
    "assessment_scales": {
      "GAD-7": 16,
      "PHQ-9": 14
    },
    "psychosocial_stressors": ["work stress", "relationship issues"],
    "protective_factors": ["supportive family", "employed"],
    "therapist_notes": "Patient presents with anxiety and depression, good insight"
  }'

# Expected response:
# {
#   "success": true,
#   "recommendations": [
#     {
#       "modality": "Cognitive Behavioral Therapy (CBT)",
#       "confidence_score": 0.85,
#       "reasoning": "...",
#       "expected_efficacy": 0.75,
#       ...
#     },
#     ...
#   ],
#   "confidence_level": "high",
#   "generated_at": "2024-01-15T10:30:00Z"
# }
```

### 4C: Test Debugging Endpoints

```bash
# Classify scenario only
curl -X POST http://localhost:5000/classify-scenario \
  -H "Content-Type: application/json" \
  -d '{"presenting_problems": ["anxiety"], "therapist_notes": "..."}'

# Predict outcome for specific modality
curl -X POST "http://localhost:5000/predict-outcome?modality=CBT" \
  -H "Content-Type: application/json" \
  -d '{"presenting_problems": ["anxiety"], ...}'

# Check model status
curl http://localhost:5000/models/status
```

---

## Step 5: Data Extraction for Training

### 5A: Extract Training Data

```bash
cd ml-engine

# Extract data from database
python scripts/extract_training_data.py \
  --output data/training_data.csv \
  --db-host localhost \
  --db-port 5432 \
  --db-name smart_communicator \
  --db-user postgres

# This creates training_data.csv with columns:
# scenario_id, patient_id, num_presenting_problems, avg_assessment_score, ...
```

### 5B: Training Set Structure

```
Training data columns:
- scenario_id: Unique scenario identifier
- patient_id: Patient identifier
- num_presenting_problems: Count of problems
- num_dsm5_codes: Count of diagnostic codes
- num_stressors: Count of psychosocial stressors
- num_protective_factors: Count of protective factors
- avg_assessment_score: Average normalized assessment score
- recommended_modality: Target variable (therapy modality)
- outcome_score: Treatment outcome measurement
- satisfaction_score: Patient satisfaction rating
- created_at: Timestamp
```

---

## Step 6: Model Training (Phase 2B)

Once you have sufficient data, train models:

### 6A: Scenario Classifier Training

```bash
cd ml-engine

python -c "
from models.scenario_classifier import ScenarioClassifier
import pandas as pd

# Load training data
df = pd.read_csv('data/training_data.csv')

# TODO: Implement BioBERT fine-tuning
# from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments

# classifier = ScenarioClassifier()
# # Fine-tune model on your data
"
```

### 6B: Modality Recommender Training

```bash
# Train LightGBM model
python -c "
import lightgbm as lgb
import pandas as pd

# Load training data
df = pd.read_csv('data/training_data.csv')

# Prepare features and target
X = df.drop(['recommended_modality', 'scenario_id'], axis=1)
y = df['recommended_modality']

# Train model
params = {
    'objective': 'multiclass',
    'num_class': 13,  # 13 therapy modalities
    'metric': 'multi_logloss'
}

# Create LightGBM dataset
train_data = lgb.Dataset(X, label=y)

# Train model
model = lgb.train(params, train_data, num_boost_round=100)

# Save model
model.save_model('models/trained/lgb_recommender.pkl')
"
```

### 6C: Outcome Predictor Training

```bash
# Train neural network
python -c "
import tensorflow as tf
import pandas as pd

# Load training data
df = pd.read_csv('data/training_data.csv')

# Prepare features and target
X = df.drop(['outcome_score', 'scenario_id'], axis=1).values
y = df['outcome_score'].values / 100  # Normalize to 0-1

# Build model
model = tf.keras.Sequential([
    tf.keras.layers.Dense(64, activation='relu', input_shape=(X.shape[1],)),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(16, activation='relu'),
    tf.keras.layers.Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='mse', metrics=['mae'])

# Train model
model.fit(X, y, epochs=50, batch_size=32, validation_split=0.2)

# Save model
model.save('models/trained/outcome_predictor.h5')
"
```

---

## Step 7: Logging and Monitoring

### 7A: View ML Engine Logs

```bash
# Docker logs
docker logs smart-communicator-ml -f

# Local logs
tail -f ml-engine/logs/ml_engine.log
```

### 7B: Monitor Performance

```bash
# Check API response times
curl -w "@curl-format.txt" -o /dev/null -s \
  http://localhost:5000/health

# Load test (install: pip install locust)
locust -f ml-engine/tests/load_test.py
```

---

## Step 8: Troubleshooting

### Issue: ML Engine fails to connect to database

**Solution:**
```bash
# Check database is running
docker ps | grep postgres

# Check connection string in .env
psql -h localhost -U postgres -d smart_communicator -c "SELECT COUNT(*) FROM therapy_modalities;"

# If database not initialized, run:
psql -U postgres -d smart_communicator -f db/schema.sql
psql -U postgres -d smart_communicator -f db/seed.sql
```

### Issue: Slow recommendation generation

**Solution:**
```bash
# Check model loading
curl http://localhost:5000/models/status

# Profile with timing
curl -w "Total time: %{time_total}s\n" http://localhost:5000/recommend
```

### Issue: Backend cannot reach ML Engine

**Solution:**
```bash
# Check ML Engine is accessible
curl http://localhost:5000/health

# Check firewall
sudo lsof -i :5000

# Check backend .env has correct ML_ENGINE_URL
cat backend/.env | grep ML_ENGINE_URL
```

---

## Step 9: Production Deployment

### 9A: Kubernetes Deployment

```yaml
# ml-engine-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: smart-communicator-ml
spec:
  replicas: 3
  selector:
    matchLabels:
      app: smart-communicator-ml
  template:
    metadata:
      labels:
        app: smart-communicator-ml
    spec:
      containers:
      - name: ml-engine
        image: smart-communicator-ml:latest
        ports:
        - containerPort: 5000
        env:
        - name: DB_HOST
          valueFrom:
            configMapKeyRef:
              name: smart-communicator-config
              key: db.host
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
```

### 9B: Environment Configuration

```bash
# Production .env
ENV=production
ML_PORT=5000
BACKEND_URL=https://api.smartcommunicator.com
DB_HOST=postgres.smartcommunicator.internal
DB_PORT=5432
LOG_LEVEL=WARNING
CONFIDENCE_THRESHOLD=0.6
```

---

## Next Steps

1. **Test Phase 1 Locally**: Run through all endpoints with PostgreSQL available
2. **Set Up ML Engine**: Follow Steps 2-3 above for local development
3. **Extract Training Data**: Once you have clinical data, use Step 5
4. **Train Models**: Implement model training per Step 6
5. **Deploy to Production**: Use Step 9 for deployment

---

## Resources

- **ML Engine Code**: `/ml-engine/`
- **Backend Integration**: `/backend/routes/recommendations.js` (create)
- **Docker Setup**: `/docker-compose.yml`
- **Training Data Extraction**: `/ml-engine/scripts/extract_training_data.py`
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Pre-Phase 2 Prep**: `/PRE_PHASE2_PREPARATION.md`

---

**ML Engine Ready** ✅

The ML Engine microservice is fully scaffolded and ready for integration testing and model training.
