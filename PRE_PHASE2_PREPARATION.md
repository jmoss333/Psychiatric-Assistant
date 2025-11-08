# Pre-Phase 2 Preparation Guide

Complete checklist and walkthrough to prepare Smart Communicator for ML-powered therapy recommendations.

---

## Overview

Before starting Phase 2 (ML/AI recommendations), you need to:
1. ✅ Ensure Phase 1 is fully tested and working
2. ✅ Expand assessment scales (COMPLETED in this guide)
3. ✅ Add assessment scale API endpoints (COMPLETED in this guide)
4. Prepare Python environment for ML models
5. Design ML architecture and data preparation
6. Set up data pipeline for training
7. Create ML model specifications
8. Prepare integration architecture

---

## Step 1: Phase 1 Verification ✅ READY

### What You Should Have Done

- ✅ Implemented all Phase 1 features (25+ API endpoints)
- ✅ Created comprehensive database schema (13 tables)
- ✅ Set up 13 therapy modalities with evidence base
- ✅ Built flexible clinical scenario capture
- ✅ Created testing framework (31+ tests)
- ✅ Written complete documentation

### Verification Checklist

Run these commands in your local environment:

```bash
# 1. Check database setup
psql -U postgres -d smart_communicator -c "\dt"
# Should show 13+ tables

# 2. Check therapy modalities seeded
psql -U postgres -d smart_communicator -c "SELECT COUNT(*) FROM therapy_modalities;"
# Should show: 13

# 3. Check assessment scales seeded
psql -U postgres -d smart_communicator -c "SELECT COUNT(*) FROM assessment_scales;"
# Should show: 19

# 4. Install dependencies
cd backend && npm install

# 5. Start server
npm run dev
# Should start on port 3000

# 6. Run tests (in another terminal)
node test-runner.js
# Should show: ✓ Passed: 31+ (100% pass rate)

# 7. Test assessment scales endpoint
curl http://localhost:3000/api/v1/assessment-scales \
  -H "Authorization: Bearer <your-token>" | jq '.count'
# Should show: 19
```

✅ **When all of the above pass, Phase 1 is ready for Phase 2**

---

## Step 2: Assessment Scales Enhancement ✅ COMPLETED

### What Was Added

- ✅ **19 Assessment Scales** across 10 categories:
  - Depression (3): PHQ-9, BDI-II, MADRS
  - Anxiety (3): GAD-7, BAI, HAM-A
  - PTSD (3): PCL-5, CAPS-5, IES-R
  - Substance Use (3): AUDIT, DAST-10, CAGE
  - Sleep (1): PSQI
  - Functioning (2): GAF, WHODAS 2.0
  - Mania (1): YMRS
  - Psychosis (1): PANSS
  - Aggression (1): OAS
  - General (1): CGI

- ✅ **New Database Table**: `assessment_scales`
  - Full scale metadata
  - Scoring ranges & interpretations
  - Evidence base data
  - Usage guidelines

- ✅ **New API Endpoints** (`/api/v1/assessment-scales`):
  - `GET /assessment-scales` - All scales
  - `GET /assessment-scales?category={cat}` - By category
  - `GET /assessment-scales/category/{category}` - Category details
  - `GET /assessment-scales/abbreviation/{abbr}` - By abbreviation (e.g., PHQ-9)
  - `GET /assessment-scales/reference/categories` - All categories

### Apply These Changes

```bash
# 1. Update database schema with new table
psql -U postgres -d smart_communicator -f db/schema.sql

# 2. Load assessment scales seed data
psql -U postgres -d smart_communicator -f db/seed_assessment_scales.sql

# 3. Restart backend (it will auto-pick up new route)
# The app.js has been updated with assessment-scales route

# 4. Verify scales were loaded
curl http://localhost:3000/api/v1/assessment-scales/reference/categories \
  -H "Authorization: Bearer <token>"
```

---

## Step 3: Python Environment Setup

Before building ML models, set up Python environment:

### 3A. Install Python & Virtual Environment

```bash
# Check Python version (need 3.9+)
python3 --version

# Create virtual environment for ML
python3 -m venv ml-env

# Activate virtual environment
source ml-env/bin/activate  # Linux/Mac
# OR
ml-env\Scripts\activate     # Windows
```

### 3B. Install Required Python Packages

```bash
pip install --upgrade pip

# ML & Data Science
pip install numpy==1.24.3
pip install pandas==2.0.3
pip install scikit-learn==1.3.0
pip install torch==2.0.1
pip install transformers==4.32.0
pip install tensorflow==2.13.0

# NLP & Text Processing
pip install nltk==3.8.1
pip install spacy==3.6.1
pip install gensim==4.3.1

# API & Server
pip install fastapi==0.100.0
pip install uvicorn==0.23.2
pip install pydantic==2.2.0

# Database
pip install psycopg2-binary==2.9.7
pip install asyncpg==0.28.0
pip install sqlalchemy==2.0.21

# Utilities
pip install python-dotenv==1.0.0
pip install requests==2.31.0
pip install pyyaml==6.0

# Development
pip install jupyter==1.0.0
pip install pytest==7.4.0
pip install black==23.9.1
pip install flake8==6.0.0
```

### 3C. Create `requirements.txt`

```bash
pip freeze > ml-requirements.txt
```

This creates a reproducible environment setup file.

---

## Step 4: ML Architecture Design

### Overview

The ML system will have 3 main components:

```
┌─────────────────────────────────────────────────────────────┐
│           SMART COMMUNICATOR ML ARCHITECTURE                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  INPUT: Clinical Scenario & Assessment Scales        │  │
│  │  ↓                                                    │  │
│  │  ┌─────────────────────────────────────────────────┐ │  │
│  │  │ 1. SCENARIO CLASSIFICATION (NLP)                │ │  │
│  │  │    • Fine-tuned BioBERT for clinical text       │ │  │
│  │  │    • Extracts: diagnoses, severity, context     │ │  │
│  │  │    • Output: Clinical features (embeddings)     │ │  │
│  │  └─────────────────────────────────────────────────┘ │  │
│  │                  ↓                                    │  │
│  │  ┌─────────────────────────────────────────────────┐ │  │
│  │  │ 2. MODALITY RECOMMENDER (Collaborative Filter)  │ │  │
│  │  │    • Feature extraction from:                   │ │  │
│  │  │      - Clinical features (from NLP)             │ │  │
│  │  │      - Assessment scale scores                  │ │  │
│  │  │      - Patient demographics                     │ │  │
│  │  │      - Therapist expertise                      │ │  │
│  │  │    • LightGBM/XGBoost ranking model             │ │  │
│  │  │    • Output: Top 5 recommended modalities       │ │  │
│  │  └─────────────────────────────────────────────────┘ │  │
│  │                  ↓                                    │  │
│  │  ┌─────────────────────────────────────────────────┐ │  │
│  │  │ 3. OUTCOME PREDICTOR (Neural Network)           │ │  │
│  │  │    • Predicts treatment response likelihood      │ │  │
│  │  │    • Input: recommendation + patient factors    │ │  │
│  │  │    • Output: Success probability (0-100%)       │ │  │
│  │  └─────────────────────────────────────────────────┘ │  │
│  │                  ↓                                    │  │
│  └──────────────────────────────────────────────────────┘  │
│                       ↓                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  OUTPUT: Therapy Recommendations & Guidance          │  │
│  │  • Recommended modalities with confidence scores     │  │
│  │  • Integrated therapy combinations                  │  │
│  │  • Phase-based treatment guidance                  │  │
│  │  • Predicted success metrics                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 4A. Model 1: Clinical Scenario Classifier

**Purpose**: Extract clinical features from unstructured/structured text

**Architecture**:
```
Input: Clinical scenario text/data
    ↓
BioBERT (fine-tuned on psychiatric data)
    ↓
Output:
  - Clinical embeddings (768-dim vector)
  - Extracted entities:
    * Diagnoses (DSM-5 codes)
    * Severity scores
    * Symptoms
    * Context factors
```

**Training Data Needed**:
- 500+ annotated clinical scenarios
- DSM-5 code labels
- Symptom/severity annotations
- Medical entity labels

**Libraries**: `transformers`, `torch`

### 4B. Model 2: Modality Recommender

**Purpose**: Recommend therapy modalities based on clinical features

**Architecture**:
```
Input Features:
  - Clinical embeddings (from Model 1)
  - Assessment scale scores (PHQ-9, GAD-7, etc.)
  - Patient demographics (age, gender, prior treatment)
  - Therapist expertise (trained modalities)
  - DSM-5 diagnoses
    ↓
Feature Engineering:
  - Normalize assessment scores
  - Encode categorical features
  - Create interaction features
    ↓
LightGBM Ranker:
  - Rank 13 therapy modalities
  - Output: Top 5 with confidence scores
    ↓
Output: Modality recommendations [{"modality": "CBT", "confidence": 0.92}, ...]
```

**Training Data Needed**:
- 1000+ patient-modality-outcome triplets
- Assessment scale history
- Treatment outcomes (success/failure)
- Therapist expertise data

**Libraries**: `lightgbm`, `scikit-learn`, `pandas`

### 4C. Model 3: Outcome Predictor

**Purpose**: Predict likelihood of treatment success

**Architecture**:
```
Input:
  - Selected modality
  - Patient features
  - Clinical severity
  - Assessment scores
    ↓
Neural Network:
  Dense layers: 128 → 64 → 32 → 16
  Activation: ReLU
  Dropout: 0.3
    ↓
Output Layer:
  Sigmoid activation
  Binary classification: Success/Failure

  Output: Probability (0-100%)
```

**Training Data Needed**:
- 2000+ treatment outcomes
- Success/failure labels
- Patient and treatment features
- Timeline data (how long to success)

**Libraries**: `tensorflow`/`torch`

---

## Step 5: Data Preparation Pipeline

### 5A. Data Collection Strategy

You'll collect data from Phase 1 usage:

```bash
# After therapists use the system:

1. Clinical Scenarios
   - Collect from clinical_scenarios table
   - Extract text features
   - Annotate with treatment outcome

2. Assessment Scales
   - Track assessment_scales scores over time
   - Correlate with treatment outcomes
   - Build longitudinal dataset

3. Outcomes
   - Track session_outcomes
   - Measure: symptom improvement, engagement, satisfaction
   - Link to modality used

4. Effectiveness Data
   - Therapist feedback (recommendation_followed)
   - Patient response (outcome_feedback)
   - Long-term outcomes (3-6 month follow-up)
```

### 5B. Data Extraction Script Template

```python
# ml-engine/data_extraction.py

import psycopg2
import pandas as pd
from datetime import datetime, timedelta

def extract_training_data():
    """Extract patient-modality-outcome data for ML training"""

    conn = psycopg2.connect(
        dbname="smart_communicator",
        user="postgres",
        password="...",
        host="localhost"
    )

    # Query: scenarios with assessment scales and outcomes
    query = """
    SELECT
        cs.scenario_id,
        cs.raw_input,
        cs.presenting_problems,
        cs.dsm5_codes,
        cs.assessment_scales,
        ts.actually_used_modality_id,
        so.long_term_improvement,
        so.modality_helpful,
        up.demographics
    FROM clinical_scenarios cs
    JOIN therapy_sessions ts ON cs.scenario_id = ts.scenario_id
    JOIN session_outcomes so ON ts.session_id = so.session_id
    JOIN unified_patient_profiles up ON cs.patient_id = up.patient_id
    WHERE cs.created_at > now() - interval '6 months'
    """

    df = pd.read_sql(query, conn)
    df.to_csv('training_data.csv', index=False)
    conn.close()
    return df

if __name__ == '__main__':
    data = extract_training_data()
    print(f"Extracted {len(data)} training samples")
```

---

## Step 6: ML Model Specifications

### 6A. NLP Model (BioBERT Fine-tuning)

**File**: `ml-engine/models/clinical_classifier.py`

```python
from transformers import AutoTokenizer, AutoModel, TrainingArguments, Trainer
import torch

class ClinicalScenarioClassifier:
    """Fine-tune BioBERT for clinical scenario classification"""

    def __init__(self):
        self.model_name = "dmis-lab/biobert-v1.1"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name)

    def prepare_training_data(self, df):
        """Prepare dataset for fine-tuning"""
        # Tokenize clinical scenarios
        # Create DSM-5 code labels
        # Split train/val/test
        pass

    def train(self, training_data):
        """Fine-tune on clinical data"""
        # Set up training arguments
        # Create Trainer
        # Train and evaluate
        pass

    def extract_features(self, scenario_text):
        """Extract clinical features from scenario"""
        # Tokenize and encode
        # Get BERT embeddings
        # Return feature vector
        pass
```

### 6B. Recommender Model (LightGBM)

**File**: `ml-engine/models/modality_recommender.py`

```python
import lightgbm as lgb
from sklearn.preprocessing import StandardScaler
import numpy as np

class ModalityRecommender:
    """Recommend therapy modalities using LightGBM"""

    def __init__(self, n_modalities=13):
        self.n_modalities = n_modalities
        self.models = {}  # One model per modality
        self.feature_names = None

    def prepare_features(self, scenarios_df, scales_df):
        """Create feature matrix"""
        # Combine scenario, assessment, and patient features
        # Feature engineering (normalization, interaction terms)
        # Return X (features), y (modality success)
        pass

    def train(self, X_train, y_train):
        """Train LightGBM ranker"""
        # Train one binary classifier per modality
        # Evaluate on validation set
        pass

    def recommend(self, features, top_k=5):
        """Get top-k modality recommendations"""
        # Score all modalities
        # Return top-k with confidence scores
        return [
            {"modality": "CBT", "confidence": 0.92},
            {"modality": "DBT", "confidence": 0.85},
            ...
        ]
```

### 6C. Outcome Prediction Model (Neural Network)

**File**: `ml-engine/models/outcome_predictor.py`

```python
import tensorflow as tf
from tensorflow import keras

class OutcomePredictive:
    """Predict treatment success using neural networks"""

    def __init__(self):
        self.model = self._build_model()

    def _build_model(self):
        """Build neural network architecture"""
        model = keras.Sequential([
            keras.layers.Dense(128, activation='relu', input_shape=(50,)),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dense(16, activation='relu'),
            keras.layers.Dense(1, activation='sigmoid')
        ])
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy', 'auc']
        )
        return model

    def train(self, X_train, y_train, epochs=20):
        """Train outcome prediction model"""
        self.model.fit(X_train, y_train, epochs=epochs, batch_size=32)

    def predict(self, features):
        """Predict treatment success probability"""
        probability = self.model.predict(features)[0][0]
        return int(probability * 100)  # Return 0-100
```

---

## Step 7: Integration Architecture

### 7A. ML Microservice Structure

```
ml-engine/
├── main.py                    # FastAPI server
├── models/
│   ├── clinical_classifier.py # NLP model
│   ├── modality_recommender.py
│   └── outcome_predictor.py
├── ml-requirements.txt
├── config.py
└── data/
    ├── training_data.csv
    └── models/
        ├── clinical_bert.pth
        ├── modality_ranker.pkl
        └── outcome_nn.h5
```

### 7B. FastAPI Server Template

```python
# ml-engine/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from models import ClinicalScenarioClassifier, ModalityRecommender, OutcomePredictor

app = FastAPI(title="Smart Communicator ML Engine", version="1.0")

# Load models
classifier = ClinicalScenarioClassifier()
recommender = ModalityRecommender()
predictor = OutcomePredictor()

class ScenarioRequest(BaseModel):
    scenario_text: str
    assessment_scales: dict
    patient_features: dict

class RecommendationResponse(BaseModel):
    modalities: list
    integrated_suggestions: list
    outcome_predictions: dict

@app.post("/recommend")
async def get_recommendations(request: ScenarioRequest):
    """Get therapy recommendations for clinical scenario"""

    try:
        # 1. Extract clinical features
        features = classifier.extract_features(request.scenario_text)

        # 2. Get modality recommendations
        recommendations = recommender.recommend(features, top_k=5)

        # 3. Predict outcomes for top modalities
        outcomes = {}
        for rec in recommendations:
            outcome_prob = predictor.predict(features)
            outcomes[rec["modality"]] = outcome_prob

        return RecommendationResponse(
            modalities=recommendations,
            outcome_predictions=outcomes
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 7C. Integration with Express Backend

```javascript
// backend/routes/recommendations.js

const axios = require('axios');

const ML_ENGINE_URL = process.env.ML_ENGINE_URL || 'http://localhost:8000';

router.post('/recommend', authenticateToken, async (req, res) => {
  try {
    const { scenario_id } = req.body;

    // Get scenario from database
    const scenario = await pool.query(
      'SELECT * FROM clinical_scenarios WHERE scenario_id = $1',
      [scenario_id]
    );

    // Call ML engine
    const mlResponse = await axios.post(`${ML_ENGINE_URL}/recommend`, {
      scenario_text: scenario.rows[0].raw_input,
      assessment_scales: scenario.rows[0].assessment_scales,
      patient_features: scenario.rows[0].presenting_problems
    });

    // Save recommendations to database
    const recResult = await pool.query(
      `INSERT INTO recommendations
       (scenario_id, recommended_modalities, outcome_predictions)
       VALUES ($1, $2, $3)
       RETURNING *`,
      [scenario_id, JSON.stringify(mlResponse.data.modalities),
       JSON.stringify(mlResponse.data.outcome_predictions)]
    );

    res.json({ recommendation: recResult.rows[0] });
  } catch (error) {
    console.error('Error getting recommendations:', error);
    res.status(500).json({ error: 'Failed to get recommendations' });
  }
});
```

---

## Step 8: Pre-Phase 2 Checklist

### Database Ready
- [ ] Phase 1 schema complete (13 tables)
- [ ] Assessment scales table created
- [ ] 19 assessment scales seeded
- [ ] Therapy modalities seeded (13 modalities)

### API Ready
- [ ] All Phase 1 endpoints working
- [ ] Assessment scales endpoints implemented
- [ ] Recommendations table created
- [ ] Tests passing (31+ tests, 100% pass rate)

### Python Environment Ready
- [ ] Python 3.9+ installed
- [ ] Virtual environment created (`ml-env`)
- [ ] ML packages installed
- [ ] `ml-requirements.txt` created

### ML Architecture Designed
- [ ] NLP model spec (BioBERT fine-tuning)
- [ ] Recommender spec (LightGBM ranking)
- [ ] Outcome predictor spec (Neural network)
- [ ] Data preparation pipeline documented

### Integration Planned
- [ ] ML microservice architecture designed
- [ ] FastAPI server template ready
- [ ] Backend integration points identified
- [ ] Database schema for ML outputs ready

---

## Troubleshooting Common Issues

### Issue: Python imports failing
```bash
# Activate virtual environment
source ml-env/bin/activate

# Reinstall packages
pip install -r ml-requirements.txt --force-reinstall
```

### Issue: Database connection from ML engine
```python
# Test connection in Python
import psycopg2
conn = psycopg2.connect(
    dbname="smart_communicator",
    user="postgres",
    password="...",
    host="localhost"
)
print("Connected!")
```

### Issue: Assessment scales endpoint not working
```bash
# Restart backend
npm run dev

# Check schema was updated
psql -U postgres -d smart_communicator -c "\dt assessment_scales"

# Check seed data
psql -U postgres -d smart_communicator -c "SELECT COUNT(*) FROM assessment_scales;"
```

---

## What's Next (Phase 2)

Once pre-Phase 2 preparation is complete:

1. **Week 1-2**: Collect initial training data from Phase 1
2. **Week 3-4**: Fine-tune NLP model (BioBERT)
3. **Week 5-6**: Train modality recommender (LightGBM)
4. **Week 7-8**: Train outcome predictor (Neural net)
5. **Week 9-10**: ML microservice integration
6. **Week 11-12**: Testing and validation

---

**Pre-Phase 2 Checklist**: Start here
**Expected Timeline**: 1-2 weeks of preparation before Phase 2
**ML Phase Expected Duration**: 8-12 weeks for complete implementation
