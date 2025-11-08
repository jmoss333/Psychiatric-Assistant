"""
Scenario Classifier Model

Classifies clinical scenarios using fine-tuned BioBERT
Categories:
- acute_crisis: Immediate safety concerns, psychiatric emergencies
- ongoing_symptom_management: Chronic mental health conditions
- trauma_focused: PTSD, complex trauma, abuse history
- substance_related: Addiction, substance use disorders
- relational: Interpersonal issues, family dynamics
- identity_development: Self-esteem, identity exploration
"""

import numpy as np
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class ScenarioClassifier:
    """
    Classifies clinical scenarios into treatment categories
    """

    def __init__(self):
        """Initialize classifier"""
        self.scenario_types = {
            "acute_crisis": "Immediate safety concerns, psychiatric emergencies",
            "ongoing_symptom_management": "Chronic mental health conditions",
            "trauma_focused": "PTSD, complex trauma, abuse history",
            "substance_related": "Addiction, substance use disorders",
            "relational": "Interpersonal issues, family dynamics",
            "identity_development": "Self-esteem, identity exploration"
        }

        # TODO: Load fine-tuned BioBERT model
        # from transformers import AutoTokenizer, AutoModelForSequenceClassification
        # self.model = AutoModelForSequenceClassification.from_pretrained(
        #     "path/to/fine-tuned/biobert"
        # )
        # self.tokenizer = AutoTokenizer.from_pretrained("path/to/fine-tuned/biobert")

    def classify(self, scenario) -> Dict[str, float]:
        """
        Classify clinical scenario

        Args:
            scenario: ClinicalScenario object with clinical data

        Returns:
            Dict mapping scenario type to probability (0-1)
        """
        try:
            # Prepare text for classification
            text = self._prepare_text(scenario)

            # TODO: Use BioBERT to classify
            # Use fine-tuned model for classification
            # inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
            # outputs = self.model(**inputs)
            # logits = outputs.logits
            # probabilities = softmax(logits)

            # Fallback: Rule-based classification (simple heuristics)
            probabilities = self._rule_based_classify(scenario)

            return probabilities

        except Exception as e:
            logger.error(f"Error classifying scenario: {e}")
            # Return uniform distribution on error
            return {k: 1/len(self.scenario_types) for k in self.scenario_types}

    def _prepare_text(self, scenario) -> str:
        """Prepare clinical text for model input"""
        text_parts = []

        # Add presenting problems
        if scenario.presenting_problems:
            text_parts.append(
                "Presenting problems: " + ", ".join(scenario.presenting_problems)
            )

        # Add diagnostic codes
        if scenario.dsm5_codes:
            text_parts.append(
                "DSM-5 codes: " + ", ".join(scenario.dsm5_codes)
            )

        # Add stressors
        if scenario.psychosocial_stressors:
            text_parts.append(
                "Stressors: " + ", ".join(scenario.psychosocial_stressors)
            )

        # Add trauma history
        if scenario.trauma_history:
            text_parts.append(f"Trauma history: {scenario.trauma_history}")

        # Add substance use
        if scenario.substance_use:
            text_parts.append(
                "Substance use: " + str(scenario.substance_use)
            )

        # Add therapist notes
        if scenario.therapist_notes:
            text_parts.append(f"Clinical notes: {scenario.therapist_notes}")

        return " ".join(text_parts)

    def _rule_based_classify(self, scenario) -> Dict[str, float]:
        """
        Simple rule-based classification for bootstrapping

        TODO: Replace with fine-tuned BioBERT model
        """
        scores = {k: 0.0 for k in self.scenario_types}

        # Check for crisis indicators
        crisis_keywords = [
            "suicide", "homicide", "self-harm", "cutting",
            "overdose", "emergency", "crisis", "acute", "severe"
        ]
        crisis_score = 0
        if scenario.therapist_notes:
            crisis_score += sum(
                1 for kw in crisis_keywords
                if kw.lower() in scenario.therapist_notes.lower()
            )
        if scenario.presenting_problems:
            crisis_score += sum(
                1 for kw in crisis_keywords
                if any(kw.lower() in p.lower() for p in scenario.presenting_problems)
            )
        if crisis_score > 0:
            scores["acute_crisis"] += min(crisis_score * 0.3, 0.7)

        # Check for trauma keywords
        trauma_keywords = [
            "trauma", "ptsd", "abuse", "assault", "violence",
            "flashback", "nightmare", "rape", "molestation"
        ]
        trauma_score = sum(
            1 for kw in trauma_keywords
            if scenario.therapist_notes and kw.lower() in scenario.therapist_notes.lower()
        )
        if trauma_score > 0:
            scores["trauma_focused"] += min(trauma_score * 0.3, 0.7)

        # Check for substance use
        if scenario.substance_use and len(scenario.substance_use) > 0:
            scores["substance_related"] += 0.5

        # Check for relational issues
        relational_keywords = [
            "relationship", "family", "conflict", "partner", "spouse",
            "divorce", "communication", "attachment", "interpersonal"
        ]
        relational_score = sum(
            1 for kw in relational_keywords
            if scenario.therapist_notes and kw.lower() in scenario.therapist_notes.lower()
        )
        if relational_score > 0:
            scores["relational"] += min(relational_score * 0.2, 0.6)

        # Default to ongoing symptom management if no strong indicators
        if sum(scores.values()) == 0:
            scores["ongoing_symptom_management"] = 0.6

        # Normalize scores to probabilities
        total = sum(scores.values())
        if total == 0:
            total = 1

        scores = {k: v / total for k, v in scores.items()}

        return scores
