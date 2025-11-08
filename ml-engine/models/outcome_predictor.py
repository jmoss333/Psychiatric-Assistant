"""
Outcome Prediction Model

Predicts treatment outcomes using neural network
Estimates:
1. Probability of treatment success
2. Number of sessions to meaningful improvement
3. Expected improvement markers
"""

import numpy as np
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class OutcomePredictor:
    """
    Predicts treatment outcomes for recommended modalities
    """

    def __init__(self):
        """Initialize outcome predictor"""
        # TODO: Load trained neural network model
        # import tensorflow as tf
        # self.model = tf.keras.models.load_model("path/to/trained/model.h5")

    def predict(
        self,
        scenario,
        recommendations: List
    ) -> Dict:
        """
        Predict outcomes for each recommended modality

        Args:
            scenario: ClinicalScenario object
            recommendations: List of ModalityRecommendation objects

        Returns:
            Dict mapping modality to OutcomePrediction
        """
        predictions = {}

        for rec in recommendations:
            try:
                pred = self.predict_single(scenario, rec.modality)
                predictions[rec.modality] = pred
            except Exception as e:
                logger.error(f"Error predicting outcome for {rec.modality}: {e}")

        return predictions

    def predict_single(
        self,
        scenario,
        modality: str
    ):
        """
        Predict outcome for single modality

        Args:
            scenario: ClinicalScenario object
            modality: Therapy modality name

        Returns:
            OutcomePrediction object
        """
        from main import OutcomePrediction

        try:
            # Extract features for prediction
            features = self._extract_features(scenario, modality)

            # TODO: Use trained neural network to predict
            # success_prob = self.model.predict(features)[0][0]

            # Fallback: Rule-based prediction
            success_prob = self._rule_based_prediction(scenario, modality)
            session_count = self._estimate_sessions(scenario, modality, success_prob)
            markers = self._expected_markers(scenario, modality)

            return OutcomePrediction(
                modality=modality,
                success_probability=success_prob,
                estimated_session_count=session_count,
                improvement_markers=markers,
            )

        except Exception as e:
            logger.error(f"Error in predict_single: {e}")
            # Return conservative prediction
            return OutcomePrediction(
                modality=modality,
                success_probability=0.5,
                estimated_session_count=12,
                improvement_markers=["Reduced symptom severity", "Improved coping"],
            )

    def _extract_features(self, scenario, modality: str) -> np.ndarray:
        """
        Extract features for neural network prediction

        TODO: Implement comprehensive feature engineering:
        - Patient demographics (age, gender, education)
        - Clinical severity (PHQ-9, GAD-7 scores)
        - Symptom type alignment with modality
        - Previous treatment history
        - Motivation and insight level
        - Comorbidity count
        """
        features = []

        # Symptom count
        symptom_count = len(scenario.presenting_problems) if scenario.presenting_problems else 0
        features.append(min(symptom_count / 5, 1.0))  # Normalize

        # Severity (from assessment scales if available)
        avg_severity = 0.5  # Default
        if scenario.assessment_scales:
            severities = list(scenario.assessment_scales.values())
            avg_severity = np.mean(severities) / 100.0  # Normalize to 0-1

        features.append(avg_severity)

        # Stressor count
        stressor_count = len(scenario.psychosocial_stressors) if scenario.psychosocial_stressors else 0
        features.append(min(stressor_count / 5, 1.0))

        # Protective factors count
        protective_count = len(scenario.protective_factors) if scenario.protective_factors else 0
        features.append(min(protective_count / 5, 1.0))

        # Substance use (risk factor)
        substance_risk = 0.3 if scenario.substance_use and len(scenario.substance_use) > 0 else 0
        features.append(substance_risk)

        # Trauma history (complexity factor)
        trauma_risk = 0.3 if scenario.trauma_history else 0
        features.append(trauma_risk)

        # Previous modality experience (if available)
        prev_mod_count = len(scenario.previous_modalities) if scenario.previous_modalities else 0
        features.append(min(prev_mod_count / 5, 1.0))

        # Modality-specific alignment
        alignment = self._modality_alignment_score(scenario, modality)
        features.append(alignment)

        return np.array(features).reshape(1, -1)

    def _rule_based_prediction(self, scenario, modality: str) -> float:
        """
        Rule-based outcome prediction

        TODO: Replace with trained neural network
        """
        base_success = 0.65  # Base success rate for any modality

        # Positive factors (increase success)
        positive_factors = 0

        # Has identified protective factors
        if scenario.protective_factors and len(scenario.protective_factors) > 0:
            positive_factors += 0.1

        # Has clear treatment goals
        if scenario.treatment_goals and len(scenario.treatment_goals) > 0:
            positive_factors += 0.05

        # Has social support (inferred from protective factors)
        if scenario.protective_factors:
            social_keywords = ["family", "friend", "support", "spouse", "partner"]
            if any(kw in str(scenario.protective_factors).lower() for kw in social_keywords):
                positive_factors += 0.05

        # Negative factors (decrease success)
        negative_factors = 0

        # Active substance use
        if scenario.substance_use and len(scenario.substance_use) > 0:
            negative_factors += 0.15

        # Significant trauma
        if scenario.trauma_history:
            negative_factors += 0.10

        # High symptom burden
        symptom_count = len(scenario.presenting_problems) if scenario.presenting_problems else 0
        if symptom_count > 5:
            negative_factors += 0.10

        # Calculate modality-specific adjustments
        modality_adjustment = self._modality_alignment_score(scenario, modality) - 0.5

        # Final calculation
        success_prob = base_success + positive_factors - negative_factors + (modality_adjustment * 0.1)

        # Clamp to valid probability range
        return max(0.2, min(0.95, success_prob))

    def _modality_alignment_score(self, scenario, modality: str) -> float:
        """Score how well modality aligns with scenario (0-1)"""
        modality_alignments = {
            "Cognitive Behavioral Therapy (CBT)": [
                "depression", "anxiety", "panic", "ocd", "ptsd", "phobia"
            ],
            "Dialectical Behavior Therapy (DBT)": [
                "suicidal", "self-harm", "borderline", "emotion dysregulation"
            ],
            "Eye Movement Desensitization & Reprocessing (EMDR)": [
                "ptsd", "trauma", "abuse", "assault", "violence"
            ],
            "Motivational Interviewing": [
                "substance", "addiction", "ambivalence", "resistance"
            ],
            "Interpersonal Therapy (IPT)": [
                "depression", "relationship", "grief", "interpersonal"
            ],
            "Psychodynamic Psychotherapy": [
                "personality", "attachment", "unconscious", "defense"
            ],
            "Acceptance and Commitment Therapy (ACT)": [
                "anxiety", "chronic pain", "acceptance", "values"
            ],
            "Emotion-Focused Therapy (EFT)": [
                "relationship", "emotion", "attachment", "intimacy"
            ],
        }

        keywords = modality_alignments.get(modality, [])
        if not keywords:
            return 0.5

        # Check presenting problems
        matches = 0
        total_keywords = len(keywords)

        if scenario.presenting_problems:
            for problem in scenario.presenting_problems:
                for kw in keywords:
                    if kw.lower() in problem.lower():
                        matches += 1
                        break

        # Check DSM-5 codes
        if scenario.dsm5_codes:
            for code in scenario.dsm5_codes:
                for kw in keywords:
                    if kw.lower() in code.lower():
                        matches += 1
                        break

        # Calculate alignment (with diminishing returns)
        if total_keywords > 0:
            alignment = min(matches / total_keywords, 1.0)
        else:
            alignment = 0.5

        return alignment

    def _estimate_sessions(self, scenario, modality: str, success_prob: float) -> int:
        """Estimate number of sessions to meaningful improvement"""
        # Base session counts by modality
        base_sessions = {
            "Cognitive Behavioral Therapy (CBT)": 12,
            "Dialectical Behavior Therapy (DBT)": 26,
            "Eye Movement Desensitization & Reprocessing (EMDR)": 8,
            "Motivational Interviewing": 4,
            "Interpersonal Therapy (IPT)": 12,
            "Psychodynamic Psychotherapy": 20,
            "Acceptance and Commitment Therapy (ACT)": 12,
            "Emotion-Focused Therapy (EFT)": 12,
            "Supportive Psychotherapy": 8,
        }

        sessions = base_sessions.get(modality, 12)

        # Adjust based on symptom severity
        if scenario.assessment_scales:
            avg_severity = np.mean(list(scenario.assessment_scales.values()))
            if avg_severity > 70:  # High severity
                sessions = int(sessions * 1.5)
            elif avg_severity < 40:  # Low severity
                sessions = int(sessions * 0.7)

        # Adjust based on success probability
        if success_prob < 0.5:
            sessions = int(sessions * 1.3)

        return sessions

    def _expected_markers(self, scenario, modality: str) -> List[str]:
        """Expected improvement markers for modality"""
        common_markers = [
            "Reduced symptom severity",
            "Improved daily functioning",
            "Better coping skills",
            "Increased insight",
        ]

        modality_markers = {
            "Cognitive Behavioral Therapy (CBT)": [
                "Reduced negative thoughts",
                "Behavioral activation",
                "Problem-solving skills",
            ],
            "Dialectical Behavior Therapy (DBT)": [
                "Reduced self-harm urges",
                "Improved emotion regulation",
                "Reduced impulsivity",
            ],
            "Eye Movement Desensitization & Reprocessing (EMDR)": [
                "Reduced trauma triggers",
                "Decreased avoidance",
                "Improved sense of safety",
            ],
            "Motivational Interviewing": [
                "Increased readiness for change",
                "Reduced ambivalence",
                "Commitment to goals",
            ],
            "Interpersonal Therapy (IPT)": [
                "Improved relationships",
                "Better communication",
                "Reduced grief/loss impact",
            ],
        }

        markers = common_markers + modality_markers.get(modality, [])
        return markers[:5]  # Return top 5 markers
