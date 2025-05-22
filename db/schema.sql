-- Unified patient profile across all three modules
CREATE TABLE unified_patient_profiles (
    patient_id UUID PRIMARY KEY,
    demographics JSONB NOT NULL,
    clinical_profile JSONB NOT NULL,
    group_therapy_history JSONB,
    intervention_response_patterns JSONB,
    aftercare_plan JSONB,
    outcome_measurements JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Cross-module analytics table
CREATE TABLE integrated_analytics (
    analytics_id UUID PRIMARY KEY,
    patient_id UUID REFERENCES unified_patient_profiles(patient_id),
    module_source VARCHAR(50),
    metric_type VARCHAR(100),
    metric_value JSONB,
    correlation_data JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- 6-Month outcome tracking
CREATE TABLE long_term_outcomes (
    patient_id UUID PRIMARY KEY,
    therapy_attendance_rate DECIMAL(3,2),
    symptom_improvement_score INTEGER,
    functional_improvement_rating INTEGER,
    quality_of_life_assessment JSONB,
    employment_status VARCHAR(50),
    housing_stability_score INTEGER,
    emergency_visits_count INTEGER,
    readmission_incidents INTEGER,
    medication_adherence_rate DECIMAL(3,2),
    healthcare_cost_total DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
