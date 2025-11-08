-- ============================================================================
-- CLINICAL DECISION SUPPORT SYSTEM SCHEMA
-- ============================================================================

-- ============================================================================
-- AUTHENTICATION & USER MANAGEMENT
-- ============================================================================

CREATE TABLE clinics (
    clinic_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    address JSONB, -- street, city, state, zip, country
    phone VARCHAR(20),
    email VARCHAR(255),
    license_number VARCHAR(100),
    status VARCHAR(50) DEFAULT 'active', -- active, inactive, suspended
    settings JSONB DEFAULT '{}', -- clinic-specific settings
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE therapists (
    therapist_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id UUID REFERENCES clinics(clinic_id),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    credentials JSONB, -- license_type, license_number, specialties
    expertise JSONB, -- array of therapy modalities they're trained in
    bio TEXT,
    profile_picture_url VARCHAR(500),
    phone VARCHAR(20),
    status VARCHAR(50) DEFAULT 'active', -- active, inactive
    last_login TIMESTAMP,
    preferences JSONB DEFAULT '{}', -- notification settings, etc.
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE sessions_tokens (
    token_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    therapist_id UUID REFERENCES therapists(therapist_id),
    token VARCHAR(500) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- PATIENT MANAGEMENT
-- ============================================================================

CREATE TABLE unified_patient_profiles (
    patient_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id UUID REFERENCES clinics(clinic_id),
    demographics JSONB NOT NULL, -- first_name, last_name, dob, gender, contact info
    clinical_profile JSONB NOT NULL, -- diagnoses (DSM-5 codes), symptoms, medical history
    current_presentations JSONB, -- active symptoms and concerns
    treatment_history JSONB, -- prior therapy modalities and responses
    preferences JSONB, -- modality preferences, accessibility needs, language
    consent_flags JSONB DEFAULT '{}', -- HIPAA, research participation, etc.
    status VARCHAR(50) DEFAULT 'active', -- active, inactive, discharged
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT clinic_patient_unique UNIQUE(clinic_id, patient_id)
);

-- ============================================================================
-- THERAPY MODALITIES REFERENCE
-- ============================================================================

CREATE TABLE therapy_modalities (
    modality_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE, -- e.g., "Cognitive Behavioral Therapy"
    abbreviation VARCHAR(20),
    description TEXT,
    category VARCHAR(100), -- cognitive-behavioral, psychodynamic, mindfulness, etc.
    evidence_base JSONB, -- research citations, efficacy data
    key_phases JSONB, -- phase names and goals
    core_techniques JSONB, -- array of technique names
    contraindications JSONB, -- conditions where NOT recommended
    typical_duration_weeks INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE modality_combinations (
    combination_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    primary_modality_id UUID REFERENCES therapy_modalities(modality_id),
    secondary_modality_id UUID REFERENCES therapy_modalities(modality_id),
    integration_description TEXT, -- how they're combined
    efficacy_score DECIMAL(3,2), -- 0.0-1.0, based on evidence
    condition_tags JSONB, -- which presentations benefit from this combo
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- ASSESSMENT SCALES REFERENCE
-- ============================================================================

CREATE TABLE assessment_scales (
    scale_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE, -- e.g., "Patient Health Questionnaire-9"
    abbreviation VARCHAR(20),
    description TEXT,
    category VARCHAR(100), -- depression, anxiety, ptsd, sleep, substance_use, etc.
    num_items INTEGER, -- number of questions
    score_range JSONB, -- { min: 0, max: 27 } for PHQ-9
    interpretation JSONB, -- { "0-4": "minimal", "5-9": "mild", ... }
    administration_time_minutes INTEGER, -- how long to administer
    evidence_base JSONB, -- reliability, validity, sensitivity, specificity
    use_cases JSONB, -- array of diagnoses/conditions it's used for
    languages_available JSONB, -- array of language translations
    copyright_info TEXT, -- licensing and copyright info
    reference_links JSONB, -- links to research, manual, etc.
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_scale_category ON assessment_scales(category);
CREATE INDEX idx_scale_abbreviation ON assessment_scales(abbreviation);

-- ============================================================================
-- CLINICAL SCENARIOS & INTAKE
-- ============================================================================

CREATE TABLE clinical_scenarios (
    scenario_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES unified_patient_profiles(patient_id),
    therapist_id UUID REFERENCES therapists(therapist_id),
    session_number INTEGER, -- which session of treatment

    -- Flexible input storage
    scenario_type VARCHAR(50), -- 'free_text', 'structured_form', 'import', 'transcription'
    raw_input TEXT, -- unstructured notes/transcript

    -- Structured clinical data
    presenting_problems JSONB, -- array of symptoms/concerns
    dsm5_codes JSONB, -- array of DSM-5 diagnostic codes
    symptom_severity JSONB, -- severity ratings for key symptoms
    psychosocial_stressors JSONB, -- life events, relationships, work, etc.
    protective_factors JSONB, -- strengths, support systems, coping skills

    -- Assessment scales (flexible storage)
    assessment_scales JSONB, -- { 'phq9': 15, 'gad7': 10, 'pcl5': 28, ... }

    -- Patient history context
    prior_responses JSONB, -- how patient responded to previous interventions
    family_history JSONB, -- relevant family mental health history
    substance_use JSONB, -- substance use history and current status
    trauma_history JSONB, -- trauma experiences (if disclosed)

    -- Provider context
    provider_notes TEXT, -- therapist's clinical impression
    urgent_flags JSONB DEFAULT '[]', -- safety concerns (suicidality, abuse, etc.)

    -- Metadata
    validity_window_hours INTEGER DEFAULT 24, -- how long is this scenario valid?
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- ML RECOMMENDATIONS
-- ============================================================================

CREATE TABLE recommendations (
    recommendation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id UUID REFERENCES clinical_scenarios(scenario_id),
    recommendation_date TIMESTAMP DEFAULT NOW(),
    ml_model_version VARCHAR(50), -- e.g., "v1.0", "v1.1"

    -- Top recommended modalities
    recommended_modalities JSONB NOT NULL, -- [
                                            --   { modality_id, confidence: 0.95, rationale },
                                            --   { modality_id, confidence: 0.87, rationale },
                                            --   ...
                                            -- ]

    integrated_therapy_suggestions JSONB, -- combinations of modalities

    -- Technique-level guidance
    technique_guidance JSONB, -- [
                              --   { technique_name, phase, step_by_step, tips, pitfalls }
                              -- ]

    -- Evidence & resources
    supporting_evidence JSONB, -- research links, guidelines
    patient_education_materials JSONB, -- PDFs, videos matched to modality

    -- Metadata
    confidence_score DECIMAL(3,2), -- overall confidence in recommendation
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- SESSION TRACKING
-- ============================================================================

CREATE TABLE therapy_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES unified_patient_profiles(patient_id),
    therapist_id UUID REFERENCES therapists(therapist_id),
    scenario_id UUID REFERENCES clinical_scenarios(scenario_id),

    -- Recommendation tracking
    recommendation_id UUID REFERENCES recommendations(recommendation_id),
    recommended_modality_id UUID REFERENCES therapy_modalities(modality_id),

    -- Actual session execution
    actually_used_modality_id UUID REFERENCES therapy_modalities(modality_id),
    techniques_applied JSONB, -- array of technique names used
    session_notes TEXT, -- therapist's session summary
    duration_minutes INTEGER,

    -- Session outcomes
    patient_response JSONB, -- engagement level, receptiveness, barriers
    in_session_outcome JSONB, -- immediate outcomes (insight gained, goals set, etc.)

    -- Metadata
    session_number INTEGER,
    session_date TIMESTAMP,
    recommendation_followed BOOLEAN, -- did therapist use recommended modality?
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- OUTCOME TRACKING
-- ============================================================================

CREATE TABLE session_outcomes (
    outcome_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES therapy_sessions(session_id),
    patient_id UUID REFERENCES unified_patient_profiles(patient_id),
    therapist_id UUID REFERENCES therapists(therapist_id),

    -- Short-term outcomes (post-session)
    symptom_change_score INTEGER, -- -10 to +10 (negative = worse, positive = better)
    engagement_level VARCHAR(50), -- low, moderate, high
    patient_satisfaction JSONB, -- rating, comments

    -- Follow-up outcomes (1-2 weeks)
    follow_up_date TIMESTAMP,
    follow_up_scores JSONB, -- repeat assessment scales (PHQ9, GAD7, etc.)

    -- Medium-term outcomes (2-4 weeks)
    functional_improvement VARCHAR(50), -- none, slight, moderate, significant
    symptom_trajectory JSONB, -- trend over sessions

    -- Long-term outcomes (3-6 months)
    long_term_improvement INTEGER, -- 0-100% improvement
    sustained_gains BOOLEAN,

    -- Modality effectiveness feedback
    modality_helpful BOOLEAN,
    modality_rating INTEGER, -- 1-5 scale
    clinician_adherence JSONB, -- how well therapist followed the modality

    -- Model learning (outcome vs. prediction)
    prediction_accuracy TEXT, -- was recommendation accurate?
    adjustment_notes TEXT, -- notes for model improvement

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- LONG-TERM OUTCOMES (ORIGINAL)
-- ============================================================================

CREATE TABLE long_term_outcomes (
    outcome_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES unified_patient_profiles(patient_id),
    therapist_id UUID REFERENCES therapists(therapist_id),
    treatment_period_start TIMESTAMP,
    treatment_period_end TIMESTAMP,

    -- Treatment adherence
    therapy_attendance_rate DECIMAL(3,2),
    sessions_completed INTEGER,
    sessions_missed INTEGER,

    -- Clinical outcomes
    symptom_improvement_score INTEGER,
    functional_improvement_rating INTEGER,
    quality_of_life_assessment JSONB,

    -- Functional outcomes
    employment_status VARCHAR(50),
    housing_stability_score INTEGER,
    social_engagement_score INTEGER,

    -- Healthcare utilization
    emergency_visits_count INTEGER,
    psychiatric_hospitalizations INTEGER,
    readmission_incidents INTEGER,

    -- Medication outcomes
    medication_adherence_rate DECIMAL(3,2),
    medication_changes JSONB,

    -- Healthcare cost
    healthcare_cost_total DECIMAL(10,2),

    -- Modality effectiveness (aggregate)
    primary_modality_id UUID REFERENCES therapy_modalities(modality_id),
    modality_effectiveness DECIMAL(3,2),

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- CROSS-MODULE ANALYTICS (UPDATED)
-- ============================================================================

CREATE TABLE integrated_analytics (
    analytics_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id UUID REFERENCES clinics(clinic_id),
    patient_id UUID REFERENCES unified_patient_profiles(patient_id),
    therapist_id UUID REFERENCES therapists(therapist_id),

    metric_type VARCHAR(100), -- 'modality_effectiveness', 'recommendation_accuracy', etc.
    metric_value JSONB,
    correlation_data JSONB, -- relationships between variables

    -- Aggregation
    aggregation_level VARCHAR(50), -- 'clinic', 'therapist', 'modality', 'diagnosis'
    time_period VARCHAR(50), -- 'monthly', 'quarterly', 'annual'

    timestamp TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

CREATE INDEX idx_therapist_clinic ON therapists(clinic_id);
CREATE INDEX idx_patient_clinic ON unified_patient_profiles(clinic_id);
CREATE INDEX idx_scenario_patient ON clinical_scenarios(patient_id);
CREATE INDEX idx_scenario_therapist ON clinical_scenarios(therapist_id);
CREATE INDEX idx_recommendation_scenario ON recommendations(scenario_id);
CREATE INDEX idx_session_patient ON therapy_sessions(patient_id);
CREATE INDEX idx_session_therapist ON therapy_sessions(therapist_id);
CREATE INDEX idx_outcome_patient ON session_outcomes(patient_id);
CREATE INDEX idx_outcome_session ON session_outcomes(session_id);
CREATE INDEX idx_long_term_patient ON long_term_outcomes(patient_id);
CREATE INDEX idx_analytics_clinic ON integrated_analytics(clinic_id);
CREATE INDEX idx_session_date ON therapy_sessions(session_date);
CREATE INDEX idx_scenario_date ON clinical_scenarios(created_at);
