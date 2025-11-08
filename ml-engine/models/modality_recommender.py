"""
Modality Recommender Model

Recommends therapy modalities using LightGBM
Uses:
1. Scenario classification
2. Patient profile (demographics, history)
3. Clinical presentation (symptoms, severity)
4. Evidence-based rules
"""

import numpy as np
import pandas as pd
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class ModalityRecommender:
    """
    Recommends therapy modalities based on clinical scenario
    """

    def __init__(self, db_connector):
        """
        Initialize recommender

        Args:
            db_connector: DatabaseConnector instance for therapy data
        """
        self.db_connector = db_connector
        self.modalities = None
        self.modality_combinations = None

        # Load modalities from database
        self._load_modalities()

        # TODO: Load trained LightGBM model
        # import lightgbm as lgb
        # self.model = lgb.Booster(model_file="path/to/trained/model.pkl")

    def _load_modalities(self):
        """Load therapy modalities from database"""
        try:
            # TODO: Fetch from database using db_connector
            # self.modalities = self.db_connector.query(
            #     "SELECT * FROM therapy_modalities"
            # )
            # self.modality_combinations = self.db_connector.query(
            #     "SELECT * FROM modality_combinations"
            # )

            logger.info("Therapy modalities loaded from database")
        except Exception as e:
            logger.error(f"Error loading modalities: {e}")

    def recommend(
        self,
        scenario,
        scenario_classification: Dict[str, float]
    ) -> List:
        """
        Get ranked modality recommendations

        Args:
            scenario: ClinicalScenario object
            scenario_classification: Dict of scenario type probabilities

        Returns:
            List of ModalityRecommendation objects
        """
        try:
            # Extract features
            features = self._extract_features(scenario, scenario_classification)

            # TODO: Use trained LightGBM model to rank modalities
            # scores = self.model.predict(features)

            # Fallback: Rule-based recommendations
            recommendations = self._rule_based_recommend(scenario, scenario_classification)

            # Sort by confidence score (highest first)
            recommendations.sort(
                key=lambda x: x.confidence_score,
                reverse=True
            )

            # Return top 5 recommendations
            return recommendations[:5]

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []

    def _extract_features(self, scenario, scenario_classification) -> Dict:
        """
        Extract features for ML model

        TODO: This needs to be implemented with proper feature engineering
        including:
        - Scenario classification probabilities
        - Symptom severity levels
        - Assessment scale scores (normalized)
        - Patient demographics
        - Previous modality outcomes
        """
        features = {
            "scenario_type_crisis": scenario_classification.get("acute_crisis", 0),
            "scenario_type_trauma": scenario_classification.get("trauma_focused", 0),
            "scenario_type_substance": scenario_classification.get("substance_related", 0),
            "scenario_type_relational": scenario_classification.get("relational", 0),
        }

        # Extract symptom severity (if provided)
        if scenario.symptom_severity:
            for symptom, severity in scenario.symptom_severity.items():
                features[f"symptom_{symptom}"] = severity / 10.0  # Normalize to 0-1

        # Extract assessment scale scores (if provided)
        if scenario.assessment_scales:
            for scale, score in scenario.assessment_scales.items():
                features[f"scale_{scale}"] = score / 100.0  # Normalize to 0-1

        return features

    def _rule_based_recommend(
        self,
        scenario,
        scenario_classification: Dict[str, float]
    ) -> List:
        """
        Rule-based modality recommendations

        TODO: Replace with trained LightGBM model
        """
        from datetime import datetime

        recommendations = []

        # Determine primary scenario type
        primary_type = max(scenario_classification, key=scenario_classification.get)

        # Rule-based recommendations by scenario type
        if primary_type == "acute_crisis":
            recommendations.extend([
                self._create_recommendation(
                    modality="Supportive Psychotherapy",
                    modality_id="1",
                    confidence=0.95,
                    reasoning="Supportive approach for acute distress and safety planning",
                    efficacy=0.85,
                    duration="4-8 weeks"
                ),
                self._create_recommendation(
                    modality="Motivational Interviewing",
                    modality_id="7",
                    confidence=0.70,
                    reasoning="Enhances engagement and safety buy-in in crisis",
                    efficacy=0.75,
                    duration="2-4 weeks"
                ),
            ])

        elif primary_type == "trauma_focused":
            recommendations.extend([
                self._create_recommendation(
                    modality="Eye Movement Desensitization & Reprocessing (EMDR)",
                    modality_id="10",
                    confidence=0.92,
                    reasoning="Gold standard for PTSD treatment",
                    efficacy=0.88,
                    duration="12-24 sessions"
                ),
                self._create_recommendation(
                    modality="Cognitive Behavioral Therapy (CBT)",
                    modality_id="1",
                    confidence=0.85,
                    reasoning="Cognitive processing of trauma memories",
                    efficacy=0.82,
                    duration="12-20 sessions"
                ),
                self._create_recommendation(
                    modality="Psychodynamic Psychotherapy",
                    modality_id="4",
                    confidence=0.60,
                    reasoning="Explore unconscious trauma patterns",
                    efficacy=0.70,
                    duration="6-12 months"
                ),
            ])

        elif primary_type == "substance_related":
            recommendations.extend([
                self._create_recommendation(
                    modality="Motivational Interviewing",
                    modality_id="7",
                    confidence=0.90,
                    reasoning="Resolves ambivalence about substance use",
                    efficacy=0.80,
                    duration="4-8 weeks"
                ),
                self._create_recommendation(
                    modality="Cognitive Behavioral Therapy (CBT)",
                    modality_id="1",
                    confidence=0.85,
                    reasoning="Addresses triggers and coping strategies",
                    efficacy=0.78,
                    duration="8-12 weeks"
                ),
                self._create_recommendation(
                    modality="Dialectical Behavior Therapy (DBT)",
                    modality_id="2",
                    confidence=0.65,
                    reasoning="Develops distress tolerance for substance urges",
                    efficacy=0.72,
                    duration="6-12 months"
                ),
            ])

        elif primary_type == "relational":
            recommendations.extend([
                self._create_recommendation(
                    modality="Interpersonal Therapy (IPT)",
                    modality_id="6",
                    confidence=0.88,
                    reasoning="Directly addresses interpersonal conflicts",
                    efficacy=0.80,
                    duration="12-16 sessions"
                ),
                self._create_recommendation(
                    modality="Emotion-Focused Therapy (EFT)",
                    modality_id="5",
                    confidence=0.82,
                    reasoning="Processes emotional needs in relationships",
                    efficacy=0.77,
                    duration="10-20 sessions"
                ),
            ])

        else:  # ongoing_symptom_management or identity_development
            recommendations.extend([
                self._create_recommendation(
                    modality="Cognitive Behavioral Therapy (CBT)",
                    modality_id="1",
                    confidence=0.85,
                    reasoning="Effective for most mental health conditions",
                    efficacy=0.75,
                    duration="12-20 sessions"
                ),
                self._create_recommendation(
                    modality="Acceptance and Commitment Therapy (ACT)",
                    modality_id="3",
                    confidence=0.70,
                    reasoning="Builds psychological flexibility and values alignment",
                    efficacy=0.72,
                    duration="8-16 sessions"
                ),
                self._create_recommendation(
                    modality="Existential Therapy",
                    modality_id="13",
                    confidence=0.60,
                    reasoning="Explores meaning and identity",
                    efficacy=0.65,
                    duration="6-12 months"
                ),
            ])

        return recommendations

    def _create_recommendation(
        self,
        modality: str,
        modality_id: str,
        confidence: float,
        reasoning: str,
        efficacy: float,
        duration: str,
    ):
        """Helper to create recommendation object"""
        from main import ModalityRecommendation

        return ModalityRecommendation(
            modality=modality,
            modality_id=modality_id,
            confidence_score=confidence,
            reasoning=reasoning,
            expected_efficacy=efficacy,
            estimated_duration=duration,
            key_techniques=self._get_key_techniques(modality_id),
            cautions=self._get_cautions(modality_id),
        )

    def _get_key_techniques(self, modality_id: str) -> List[str]:
        """Get key techniques for a modality"""
        techniques_map = {
            "1": ["Thought records", "Behavioral experiments", "Exposure therapy"],
            "2": ["Skills modules", "DBT worksheets", "Chain analysis"],
            "3": ["Values clarification", "Willingness exercises", "Defusion"],
            "4": ["Free association", "Dream analysis", "Transference work"],
            "5": ["Emotion validation", "Attachment focus", "Experiential"],
            "6": ["Interpersonal inventory", "Role plays", "Communication"],
            "7": ["Reflective listening", "Exploring ambivalence", "Developing discrepancy"],
            "10": ["Eye movements", "Bilateral stimulation", "EMDR protocols"],
            "13": ["Existential exploration", "Meaning-making", "Responsibility"],
        }
        return techniques_map.get(modality_id, ["Standard modality techniques"])

    def _get_cautions(self, modality_id: str) -> List[str]:
        """Get cautions for a modality"""
        cautions_map = {
            "1": ["Not first-line for active psychosis"],
            "2": ["Requires significant commitment (6+ months)", "Not for acute crisis"],
            "4": ["Not suitable for acute psychosis", "Requires psychological mindedness"],
            "10": ["Requires trained EMDR practitioner", "May destabilize without safety"],
        }
        return cautions_map.get(modality_id, [])
