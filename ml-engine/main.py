"""
Smart Communicator ML Engine - FastAPI Microservice

Phase 2: AI-powered therapy modality recommendations
Provides:
1. Clinical Scenario Classification (BioBERT)
2. Therapy Modality Recommendation (LightGBM)
3. Outcome Prediction (Neural Network)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Tuple
import logging
import os
from dotenv import load_dotenv

from models.scenario_classifier import ScenarioClassifier
from models.modality_recommender import ModalityRecommender
from models.outcome_predictor import OutcomePredictor
from utils.db_connector import DatabaseConnector

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Smart Communicator ML Engine",
    description="AI-powered therapy recommendations",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("BACKEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize models (lazy loading)
models = {
    "scenario_classifier": None,
    "modality_recommender": None,
    "outcome_predictor": None,
}

db_connector = None


# ============================================================================
# DATA MODELS
# ============================================================================

class ClinicalScenario(BaseModel):
    """Clinical scenario data for recommendation"""
    patient_id: str = Field(..., description="Patient ID")
    scenario_id: Optional[str] = Field(None, description="Scenario ID (if existing)")
    presenting_problems: List[str] = Field(..., description="List of presenting problems")
    dsm5_codes: Optional[List[str]] = Field(None, description="DSM-5 diagnostic codes")
    symptom_severity: Optional[Dict[str, float]] = Field(None, description="Symptom severity ratings (0-10)")
    assessment_scales: Optional[Dict[str, float]] = Field(None, description="Assessment scale scores")
    psychosocial_stressors: Optional[List[str]] = Field(None, description="Current stressors")
    protective_factors: Optional[List[str]] = Field(None, description="Patient strengths")
    trauma_history: Optional[str] = Field(None, description="Trauma background")
    substance_use: Optional[Dict[str, str]] = Field(None, description="Current substance use")
    therapist_notes: Optional[str] = Field(None, description="Therapist clinical notes")
    previous_modalities: Optional[List[str]] = Field(None, description="Previously tried modalities")
    treatment_goals: Optional[List[str]] = Field(None, description="Patient treatment goals")


class ModalityRecommendation(BaseModel):
    """Recommendation for a therapy modality"""
    modality: str = Field(..., description="Therapy modality name")
    modality_id: str = Field(..., description="Database ID")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence score (0-1)")
    reasoning: str = Field(..., description="Why this modality recommended")
    expected_efficacy: float = Field(..., ge=0, le=1, description="Expected treatment efficacy")
    estimated_duration: str = Field(..., description="Estimated treatment duration")
    key_techniques: List[str] = Field(..., description="Key techniques for this modality")
    cautions: Optional[List[str]] = Field(None, description="Important cautions")


class OutcomePrediction(BaseModel):
    """Prediction of treatment outcome"""
    modality: str = Field(..., description="Therapy modality")
    success_probability: float = Field(..., ge=0, le=1, description="Probability of treatment success")
    estimated_session_count: int = Field(..., description="Estimated sessions to improvement")
    improvement_markers: List[str] = Field(..., description="Expected improvement signs")


class RecommendationResponse(BaseModel):
    """Complete recommendation response"""
    scenario_id: str = Field(..., description="Scenario ID")
    patient_id: str = Field(..., description="Patient ID")
    scenario_classification: Dict[str, float] = Field(..., description="Scenario type probabilities")
    recommendations: List[ModalityRecommendation] = Field(..., description="Ranked modality recommendations")
    outcome_predictions: Dict[str, OutcomePrediction] = Field(..., description="Outcome predictions per modality")
    confidence_level: str = Field(..., description="Overall confidence (high/medium/low)")
    generated_at: str = Field(..., description="Timestamp of generation")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def load_models():
    """Load ML models on startup"""
    global models, db_connector

    try:
        logger.info("Loading ML models...")

        # Initialize database connector
        db_connector = DatabaseConnector(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 5432)),
            database=os.getenv("DB_NAME", "smart_communicator"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "")
        )

        # Load scenario classifier
        models["scenario_classifier"] = ScenarioClassifier()
        logger.info("✓ Scenario Classifier loaded")

        # Load modality recommender
        models["modality_recommender"] = ModalityRecommender(db_connector)
        logger.info("✓ Modality Recommender loaded")

        # Load outcome predictor
        models["outcome_predictor"] = OutcomePredictor()
        logger.info("✓ Outcome Predictor loaded")

        logger.info("All models loaded successfully!")

    except Exception as e:
        logger.error(f"Error loading models: {e}")
        raise


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    load_models()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "models_loaded": all(models.values()),
        "database_connected": db_connector is not None
    }


@app.post("/recommend", response_model=RecommendationResponse)
async def recommend_modality(scenario: ClinicalScenario):
    """
    Get therapy modality recommendations for a clinical scenario

    Takes patient clinical data and returns:
    1. Clinical scenario classification
    2. Ranked therapy modality recommendations
    3. Outcome predictions per modality
    """
    try:
        logger.info(f"Processing recommendation for scenario: {scenario.scenario_id}")

        # Step 1: Classify clinical scenario
        scenario_classification = models["scenario_classifier"].classify(scenario)
        logger.info(f"Scenario classified: {scenario_classification}")

        # Step 2: Get recommendations
        recommendations = models["modality_recommender"].recommend(
            scenario=scenario,
            scenario_classification=scenario_classification
        )
        logger.info(f"Generated {len(recommendations)} recommendations")

        # Step 3: Predict outcomes
        outcome_predictions = models["outcome_predictor"].predict(
            scenario=scenario,
            recommendations=recommendations
        )
        logger.info(f"Generated outcome predictions")

        # Determine overall confidence
        avg_confidence = sum(r.confidence_score for r in recommendations) / len(recommendations)
        if avg_confidence > 0.8:
            confidence_level = "high"
        elif avg_confidence > 0.6:
            confidence_level = "medium"
        else:
            confidence_level = "low"

        from datetime import datetime

        response = RecommendationResponse(
            scenario_id=scenario.scenario_id or "new_scenario",
            patient_id=scenario.patient_id,
            scenario_classification=scenario_classification,
            recommendations=recommendations,
            outcome_predictions=outcome_predictions,
            confidence_level=confidence_level,
            generated_at=datetime.now().isoformat()
        )

        logger.info("Recommendation complete")
        return response

    except Exception as e:
        logger.error(f"Error generating recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/classify-scenario")
async def classify_scenario(scenario: ClinicalScenario):
    """Classify clinical scenario type (debugging endpoint)"""
    try:
        classification = models["scenario_classifier"].classify(scenario)
        return {
            "scenario_id": scenario.scenario_id,
            "classification": classification
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict-outcome")
async def predict_outcome(
    scenario: ClinicalScenario,
    modality: str
):
    """Predict treatment outcome for specific modality (debugging endpoint)"""
    try:
        prediction = models["outcome_predictor"].predict_single(
            scenario=scenario,
            modality=modality
        )
        return {
            "scenario_id": scenario.scenario_id,
            "modality": modality,
            "prediction": prediction
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models/status")
async def models_status():
    """Get status of all loaded models"""
    return {
        "scenario_classifier": models["scenario_classifier"] is not None,
        "modality_recommender": models["modality_recommender"] is not None,
        "outcome_predictor": models["outcome_predictor"] is not None,
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return HTTPException(status_code=400, detail=str(exc))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("ML_PORT", 5000)),
        reload=os.getenv("ENV", "production") != "production"
    )
