# Phase 2: ML-Powered Recommendations - Implementation Checklist

Complete checklist for implementing Phase 2 of Smart Communicator.

---

## Overview

Phase 2 adds machine learning-powered therapy recommendations to Smart Communicator:
- **Timeline**: 8-12 weeks
- **Key Deliverable**: End-to-end recommendation system
- **Prerequisites**: Phase 1 complete and tested

---

## Phase 2A: Foundation & Integration (Weeks 1-3)

### Week 1: Environment & Infrastructure

#### Python Environment Setup
- [ ] Create ML engine directory structure (`/ml-engine`)
  - [ ] Main application (`main.py`) ✅ Created
  - [ ] Models directory with 3 classifiers ✅ Created
  - [ ] Utilities for database connectivity ✅ Created
  - [ ] Scripts for data extraction ✅ Created

- [ ] Python dependencies installed
  - [ ] Create virtual environment: `python3 -m venv ml-env`
  - [ ] Install requirements: `pip install -r ml-engine/requirements.txt`
  - [ ] Verify installations: `pip list | grep -E "fastapi|transformers|torch|lightgbm"`

- [ ] Environment configuration
  - [ ] Copy `.env.example` to `.env`
  - [ ] Set database credentials
  - [ ] Set JWT secret matching backend
  - [ ] Verify database connectivity

#### Docker Setup
- [ ] Backend Dockerfile created ✅
- [ ] ML Engine Dockerfile created ✅
- [ ] docker-compose.yml created ✅
- [ ] Test Docker build locally
  - [ ] `docker build -t smart-communicator-backend ./backend`
  - [ ] `docker build -t smart-communicator-ml ./ml-engine`
  - [ ] `docker-compose up` starts all services

### Week 2: Backend Integration

#### Create Recommendations Route
- [ ] Create `/backend/routes/recommendations.js`
  - [ ] `POST /recommendations/scenario` - Get recommendations
  - [ ] Input validation with Joi
  - [ ] Error handling for ML engine failures

- [ ] Register route in `/backend/app.js`
  - [ ] Import recommendations router
  - [ ] Mount on `/api/v1/recommendations`

- [ ] Update `/backend/.env`
  - [ ] Add `ML_ENGINE_URL=http://localhost:5000`
  - [ ] Add `ML_ENGINE_TIMEOUT=30000`

#### Update Backend Dependencies
- [ ] Verify axios is in package.json (for HTTP calls)
- [ ] Test backend health check works
- [ ] Test backend can call ML engine health endpoint

#### Database Schema Updates
- [ ] Create `recommendations` table in database
  ```sql
  -- Add to db/schema.sql if not present
  CREATE TABLE recommendations (
    recommendation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id UUID NOT NULL REFERENCES clinical_scenarios(scenario_id),
    patient_id UUID NOT NULL REFERENCES unified_patient_profiles(patient_id),
    recommended_modalities JSONB NOT NULL,
    confidence_score FLOAT NOT NULL,
    generated_at TIMESTAMP DEFAULT NOW(),
    model_version VARCHAR(50) NOT NULL,
    FOREIGN KEY (scenario_id) REFERENCES clinical_scenarios(scenario_id),
    FOREIGN KEY (patient_id) REFERENCES unified_patient_profiles(patient_id)
  );
  ```
- [ ] Create index on scenario_id and patient_id

### Week 3: Testing & Validation

#### Integration Testing
- [ ] Start services
  - [ ] Backend: `cd backend && npm run dev`
  - [ ] ML Engine: `cd ml-engine && python main.py`
  - [ ] Database: Ensure PostgreSQL running

- [ ] Test endpoints
  - [ ] `curl http://localhost:5000/health` ✅ Should return healthy status
  - [ ] `curl http://localhost:5000/models/status` - Check models loaded
  - [ ] `curl -X POST http://localhost:3000/api/v1/recommendations/scenario ...` - Test integration

- [ ] Test error handling
  - [ ] [ ] Call with missing fields
  - [ ] [ ] Call with invalid JSON
  - [ ] [ ] Kill ML engine and test graceful failure
  - [ ] [ ] Test timeout handling

#### Documentation
- [ ] Update backend README with ML integration section
- [ ] Create ML_ENGINE_INTEGRATION_GUIDE.md ✅
- [ ] Add API documentation for new endpoints
- [ ] Create troubleshooting guide

---

## Phase 2B: Model Training (Weeks 4-6)

### Week 4: Data Preparation

#### Data Extraction
- [ ] Implement `extract_training_data.py` ✅
  - [ ] Query clinical_scenarios table
  - [ ] Extract features: symptom counts, assessment scores, stressors
  - [ ] Extract target: recommended_modality, outcome_score
  - [ ] Export to CSV

- [ ] Generate training dataset
  - [ ] Run: `python ml-engine/scripts/extract_training_data.py --output data/training_data.csv`
  - [ ] Verify CSV created with minimum 100+ samples
  - [ ] Check data quality: no null values in target column
  - [ ] Analyze class distribution (are modalities balanced?)

#### Data Validation
- [ ] Check for class imbalance
  - [ ] If severe, implement stratified sampling or class weights
- [ ] Verify feature engineering
  - [ ] Assessment scores normalized to 0-100
  - [ ] Counts of problems/stressors properly captured
  - [ ] No data leakage between train/test

### Week 5: Model Training - Scenario Classifier

#### BioBERT Fine-tuning
- [ ] Prepare BioBERT environment
  - [ ] Install transformers library: `pip install transformers==4.33.3`
  - [ ] Download pre-trained BioBERT: `transformers-cli download medical/biobert_pretrained_on_notes`
  - [ ] Create training script: `/ml-engine/training/train_scenario_classifier.py`

- [ ] Implement training pipeline
  ```python
  from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments

  # Load pre-trained model
  model_name = "microsoft/BiomedNLP-PubMedBERT-base-uncased"
  tokenizer = AutoTokenizer.from_pretrained(model_name)
  model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=6)

  # Tokenize training data
  def tokenize_function(examples):
      return tokenizer(examples["text"], padding="max_length", truncation=True)

  # Train with Hugging Face Trainer
  training_args = TrainingArguments(
      output_dir="models/trained/biobert_classifier",
      num_train_epochs=3,
      per_device_train_batch_size=8,
      per_device_eval_batch_size=8,
      warmup_steps=500,
      weight_decay=0.01,
  )
  ```

- [ ] Train model
  - [ ] [ ] Split data: 70% train, 15% validation, 15% test
  - [ ] [ ] Train for 3-5 epochs
  - [ ] [ ] Monitor validation loss (should decrease)
  - [ ] [ ] Save best model

- [ ] Evaluate on test set
  - [ ] Calculate accuracy: target ≥ 0.85
  - [ ] Calculate F1 score per class
  - [ ] Generate confusion matrix
  - [ ] Document results

- [ ] Save model
  - [ ] [ ] Export to: `models/trained/biobert_classifier/`
  - [ ] [ ] Update model path in `models/scenario_classifier.py`

### Week 6: Model Training - Modality Recommender & Outcome Predictor

#### LightGBM Modality Recommender
- [ ] Prepare feature matrix
  - [ ] Extract features from training data
  - [ ] Create one-hot encoded modality targets
  - [ ] Split: 70% train, 30% validation

- [ ] Train LightGBM
  ```python
  import lightgbm as lgb

  params = {
      'objective': 'multiclass',
      'num_class': 13,  # 13 therapy modalities
      'metric': 'multi_logloss',
      'learning_rate': 0.1,
      'num_leaves': 31,
  }

  train_data = lgb.Dataset(X_train, label=y_train)
  model = lgb.train(params, train_data, num_boost_round=100)
  ```

- [ ] Evaluate
  - [ ] Accuracy on test set: target ≥ 0.75
  - [ ] Top-5 accuracy (correct modality in top 5): target ≥ 0.90
  - [ ] Feature importance analysis

- [ ] Save model
  - [ ] Export: `models/trained/lgb_recommender.pkl`

#### Neural Network Outcome Predictor
- [ ] Build architecture
  ```python
  import tensorflow as tf

  model = tf.keras.Sequential([
      tf.keras.layers.Dense(64, activation='relu', input_shape=(num_features,)),
      tf.keras.layers.BatchNormalization(),
      tf.keras.layers.Dropout(0.3),
      tf.keras.layers.Dense(32, activation='relu'),
      tf.keras.layers.Dropout(0.2),
      tf.keras.layers.Dense(16, activation='relu'),
      tf.keras.layers.Dense(1, activation='sigmoid')  # Binary outcome
  ])

  model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
  ```

- [ ] Train model
  - [ ] Epochs: 50-100
  - [ ] Batch size: 32
  - [ ] Validation split: 20%
  - [ ] Early stopping if validation loss plateaus

- [ ] Evaluate
  - [ ] Accuracy: target ≥ 0.75
  - [ ] AUC-ROC: target ≥ 0.80
  - [ ] Calibration plot (predicted vs actual)

- [ ] Save model
  - [ ] Export: `models/trained/outcome_predictor.h5`

---

## Phase 2C: Production Integration (Weeks 7-8)

### Week 7: Load Models & Integration Testing

#### Load Trained Models
- [ ] Update model loading in `ml-engine/main.py`
  - [ ] Load BioBERT from `models/trained/biobert_classifier/`
  - [ ] Load LightGBM from `models/trained/lgb_recommender.pkl`
  - [ ] Load TensorFlow from `models/trained/outcome_predictor.h5`

- [ ] Verify model loading
  - [ ] Restart ML engine: `python main.py`
  - [ ] Check logs: "All models loaded successfully!"
  - [ ] Test `/models/status` endpoint

#### End-to-End Testing
- [ ] Test full recommendation pipeline
  ```bash
  curl -X POST http://localhost:3000/api/v1/recommendations/scenario \
    -H "Authorization: Bearer $TOKEN" \
    -d '{
      "patient_id": "test_patient",
      "presenting_problems": ["anxiety", "insomnia"],
      "assessment_scales": {"GAD-7": 18},
      ...
    }'
  ```

- [ ] Verify outputs
  - [ ] Recommendations returned (should be top 5)
  - [ ] Confidence scores between 0-1
  - [ ] Outcome predictions included
  - [ ] Response time < 5 seconds

### Week 8: Performance & Optimization

#### Performance Benchmarking
- [ ] Test latency
  - [ ] Single request: target < 2 seconds
  - [ ] 10 concurrent requests: target < 10 seconds total
  - [ ] 100 concurrent requests: monitor for timeouts

- [ ] Test accuracy
  - [ ] Run test set through API
  - [ ] Compare predictions to baseline
  - [ ] Document accuracy metrics

#### Optimization
- [ ] Model quantization (if needed)
  - [ ] Convert PyTorch models to ONNX
  - [ ] Use ONNX Runtime for faster inference
- [ ] Caching
  - [ ] Cache modality recommendations for common scenarios
  - [ ] Invalidate cache when models retrained
- [ ] Async processing
  - [ ] For slow operations, implement job queue

---

## Phase 2D: Advanced Features (Weeks 9-12)

### Week 9: Outcome Tracking

#### Database Schema
- [ ] Create `recommendation_feedback` table
  ```sql
  CREATE TABLE recommendation_feedback (
    feedback_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recommendation_id UUID REFERENCES recommendations(recommendation_id),
    modality_used VARCHAR(255),
    actual_outcome FLOAT,  -- 0-1
    patient_improvement VARCHAR(50),  -- none/slight/moderate/significant
    feedback_date TIMESTAMP DEFAULT NOW()
  );
  ```

- [ ] Create `modality_effectiveness` tracking
  ```sql
  CREATE TABLE modality_effectiveness (
    modality_id UUID,
    time_period VARCHAR(50),
    success_rate FLOAT,
    avg_sessions INT,
    updated_at TIMESTAMP DEFAULT NOW()
  );
  ```

#### Feedback Integration
- [ ] Create `/api/v1/recommendations/:id/feedback` endpoint
  - [ ] Accept actual outcome data
  - [ ] Calculate actual vs predicted
  - [ ] Update modality effectiveness scores
  - [ ] Use for continuous model improvement

### Week 10: Real-time Session Guidance

#### Backend Streaming
- [ ] Implement WebSocket for real-time updates
  - [ ] Client connects during therapy session
  - [ ] Receives real-time guidance updates
  - [ ] Displays modality-specific techniques

#### ML Engine Streaming
- [ ] Create streaming recommendation endpoint
  - [ ] Accepts real-time symptom updates
  - [ ] Returns updated recommendations
  - [ ] Maintains session context

### Week 11: Advanced Analytics

#### Dashboard Data
- [ ] Create analytics endpoints
  - [ ] `/api/v1/analytics/recommendation-accuracy` - Model performance
  - [ ] `/api/v1/analytics/modality-effectiveness` - Treatment outcomes
  - [ ] `/api/v1/analytics/therapist-insights` - By-therapist statistics

- [ ] Implement reporting
  - [ ] Monthly recommendation accuracy reports
  - [ ] Modality effectiveness trends
  - [ ] Patient outcome distributions

### Week 12: Continuous Learning

#### Model Retraining Pipeline
- [ ] Implement automated retraining
  - [ ] Weekly extraction of new data
  - [ ] Monthly model retraining
  - [ ] A/B testing of new models
  - [ ] Automatic rollout of improved models

- [ ] Version control for models
  - [ ] Tag trained models with version
  - [ ] Track model lineage and performance
  - [ ] Implement rollback mechanism

- [ ] Monitoring & Alerts
  - [ ] Monitor recommendation accuracy
  - [ ] Alert if accuracy drops below threshold
  - [ ] Log all recommendations for audit trail

---

## Pre-Phase 2 Verification Checklist ✅

Before starting Phase 2, verify Phase 1:

- [ ] **Phase 1 API Tests Pass**
  ```bash
  cd backend && node test-runner.js
  # Should show: ✓ Passed 31+, ✗ Failed 0
  ```

- [ ] **Database Fully Seeded**
  ```bash
  psql -U postgres -d smart_communicator -c "\dt"
  # Should show: 13+ tables

  psql -U postgres -d smart_communicator -c "SELECT COUNT(*) FROM therapy_modalities;"
  # Should show: 13

  psql -U postgres -d smart_communicator -c "SELECT COUNT(*) FROM assessment_scales;"
  # Should show: 19
  ```

- [ ] **Backend Running Locally**
  ```bash
  cd backend && npm run dev
  # Should start on port 3000 without errors
  ```

- [ ] **All Documentation Present**
  - [ ] `/PHASE1_COMPLETION_SUMMARY.md` ✅
  - [ ] `/PRE_PHASE2_PREPARATION.md` ✅
  - [ ] `/ASSESSMENT_SCALES_GUIDE.md` ✅
  - [ ] `/ML_ENGINE_INTEGRATION_GUIDE.md` ✅
  - [ ] `/backend/API_DOCUMENTATION.md` ✅

---

## Deliverables Checklist

### Code Artifacts
- [ ] ML Engine FastAPI application (`main.py`) ✅
- [ ] Scenario Classifier model (`models/scenario_classifier.py`) ✅
- [ ] Modality Recommender model (`models/modality_recommender.py`) ✅
- [ ] Outcome Predictor model (`models/outcome_predictor.py`) ✅
- [ ] Database connector (`utils/db_connector.py`) ✅
- [ ] Data extraction script (`scripts/extract_training_data.py`) ✅
- [ ] Backend recommendation route (`routes/recommendations.js`)
- [ ] Trained model binaries
  - [ ] BioBERT classifier
  - [ ] LightGBM recommender
  - [ ] TensorFlow outcome predictor

### Infrastructure
- [ ] Docker setup
  - [ ] Backend Dockerfile ✅
  - [ ] ML Engine Dockerfile ✅
  - [ ] docker-compose.yml ✅
- [ ] Environment configuration
  - [ ] .env templates ✅
  - [ ] Database initialization
  - [ ] Model serving configuration

### Documentation
- [ ] ML Engine Integration Guide ✅
- [ ] Model Training Documentation
- [ ] API Documentation (updated)
- [ ] Deployment Guide
- [ ] Troubleshooting Guide

### Testing & Validation
- [ ] Unit tests for models
- [ ] Integration tests
- [ ] Performance benchmarks
- [ ] Model evaluation reports

---

## Success Criteria

### Phase 2 Complete When:

1. ✅ ML Engine can be started locally or in Docker
2. ✅ All three models load without errors
3. ✅ Recommendation endpoint returns valid recommendations
4. ✅ Accuracy on test set ≥ 75%
5. ✅ Response time < 2 seconds per request
6. ✅ Models trained on real clinical data
7. ✅ End-to-end integration tested
8. ✅ Documentation complete
9. ✅ Error handling works gracefully
10. ✅ Ready for production deployment

---

## Timeline Summary

| Phase | Duration | Key Activities |
|-------|----------|-----------------|
| 2A | Weeks 1-3 | Setup, integration, testing |
| 2B | Weeks 4-6 | Data prep, model training |
| 2C | Weeks 7-8 | Load models, optimize |
| 2D | Weeks 9-12 | Advanced features, monitoring |

---

## Resources

- **ML Engine Code**: `/ml-engine/`
- **Backend Integration**: `/backend/routes/recommendations.js`
- **Training Data**: `/ml-engine/data/training_data.csv`
- **Model Training Scripts**: `/ml-engine/training/`
- **Docker Setup**: `/docker-compose.yml`
- **Documentation**: `/PRE_PHASE2_PREPARATION.md`, `/ML_ENGINE_INTEGRATION_GUIDE.md`

---

## Support & Escalation

If you encounter issues:
1. Check `/ML_ENGINE_INTEGRATION_GUIDE.md` troubleshooting section
2. Review ML Engine logs: `tail -f ml-engine/logs/ml_engine.log`
3. Test database connectivity independently
4. Verify environment variables are set correctly
5. Check backend can call ML engine health endpoint

---

**Phase 2 Ready to Start** ✅

All infrastructure, templates, and documentation are in place.
Begin with Phase 2A: Environment & Infrastructure (Week 1).
