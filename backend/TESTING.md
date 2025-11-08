# Phase 1 Testing Guide

Complete testing checklist for Smart Communicator backend Phase 1 implementation.

## Prerequisites

Before testing, ensure:
1. PostgreSQL is running
2. Database `smart_communicator` exists
3. Schema and seed data loaded
4. `.env` file configured
5. Dependencies installed (`npm install`)

### Quick Setup

```bash
# Create database
createdb smart_communicator

# Load schema
psql -U postgres -d smart_communicator -f ../db/schema.sql

# Seed data
psql -U postgres -d smart_communicator -f ../db/seed.sql

# Verify tables created
psql -U postgres -d smart_communicator -c "\dt"
```

## Starting the Server

```bash
npm run dev
```

Expected output:
```
Smart Communicator Backend listening on port 3000
Environment: development
API Documentation: http://localhost:3000/api/v1
```

## Test 1: Health Check

**Endpoint**: `GET /health`

```bash
curl http://localhost:3000/health
```

**Expected Response** (200 OK):
```json
{
  "status": "OK",
  "timestamp": "2024-01-15T10:30:45.123Z"
}
```

---

## Test 2: Authentication Flow

### 2A. Register Therapist

**Endpoint**: `POST /api/v1/auth/register`

```bash
curl -X POST http://localhost:3000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dr.smith@clinic.com",
    "password": "SecurePassword123!",
    "first_name": "John",
    "last_name": "Smith"
  }'
```

**Expected Response** (201 Created):
```json
{
  "message": "Therapist registered successfully",
  "token": "eyJhbGc...",
  "therapist": {
    "therapist_id": "uuid-here",
    "email": "dr.smith@clinic.com",
    "first_name": "John",
    "last_name": "Smith"
  }
}
```

**Save the token for subsequent tests**. Export it:
```bash
export TOKEN="your-token-here"
```

### 2B. Register Second Therapist

```bash
curl -X POST http://localhost:3000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dr.jones@clinic.com",
    "password": "AnotherPassword456!",
    "first_name": "Sarah",
    "last_name": "Jones"
  }'
```

### 2C. Login

**Endpoint**: `POST /api/v1/auth/login`

```bash
curl -X POST http://localhost:3000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dr.smith@clinic.com",
    "password": "SecurePassword123!"
  }'
```

**Expected Response** (200 OK):
```json
{
  "message": "Login successful",
  "token": "eyJhbGc...",
  "therapist": {
    "therapist_id": "uuid",
    "email": "dr.smith@clinic.com",
    "first_name": "John",
    "last_name": "Smith"
  }
}
```

### 2D. Test Invalid Password

```bash
curl -X POST http://localhost:3000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dr.smith@clinic.com",
    "password": "WrongPassword"
  }'
```

**Expected Response** (401 Unauthorized):
```json
{
  "error": "Invalid email or password"
}
```

### 2E. Test Missing Token

```bash
curl -X GET http://localhost:3000/api/v1/patients
```

**Expected Response** (401 Unauthorized):
```json
{
  "error": "Access token required"
}
```

### 2F. Logout

```bash
curl -X POST http://localhost:3000/api/v1/auth/logout \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response** (200 OK):
```json
{
  "message": "Logout successful"
}
```

---

## Test 3: Clinic Management

### 3A. Create Clinic

**Endpoint**: `POST /api/v1/clinics`

```bash
curl -X POST http://localhost:3000/api/v1/clinics \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Urban Mental Health Center",
    "address": {
      "street": "123 Main Street",
      "city": "Springfield",
      "state": "IL",
      "zip": "62701",
      "country": "USA"
    },
    "phone": "+1-217-555-0100",
    "email": "contact@urbanmh.com",
    "license_number": "IL-MH-2024-001"
  }'
```

**Expected Response** (201 Created):
```json
{
  "message": "Clinic created successfully",
  "clinic": {
    "clinic_id": "uuid",
    "name": "Urban Mental Health Center",
    "address": { ... },
    "status": "active",
    "created_at": "2024-01-15T10:30:45.123Z",
    "updated_at": "2024-01-15T10:30:45.123Z"
  }
}
```

**Save clinic_id** for patient creation:
```bash
export CLINIC_ID="your-clinic-uuid"
```

### 3B. Get Clinics

```bash
curl -X GET http://localhost:3000/api/v1/clinics \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response** (200 OK):
```json
{
  "clinics": [
    {
      "clinic_id": "uuid",
      "name": "Urban Mental Health Center",
      ...
    }
  ]
}
```

### 3C. Get Clinic by ID

```bash
curl -X GET http://localhost:3000/api/v1/clinics/$CLINIC_ID \
  -H "Authorization: Bearer $TOKEN"
```

### 3D. Update Clinic

```bash
curl -X PUT http://localhost:3000/api/v1/clinics/$CLINIC_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+1-217-555-0200",
    "status": "active"
  }'
```

**Expected Response** (200 OK):
```json
{
  "message": "Clinic updated successfully",
  "clinic": { ... }
}
```

---

## Test 4: Patient Management

### 4A. Create Patient (Basic)

**Endpoint**: `POST /api/v1/patients`

```bash
curl -X POST http://localhost:3000/api/v1/patients \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "demographics": {
      "first_name": "Jane",
      "last_name": "Doe",
      "date_of_birth": "1990-05-15",
      "gender": "female",
      "contact_email": "jane.doe@example.com",
      "contact_phone": "+1-217-555-0300"
    },
    "clinical_profile": {
      "dsm5_codes": ["F41.1", "F32.9"],
      "medical_history": "Type 2 Diabetes, Hypertension",
      "current_medications": ["Sertraline 50mg daily", "Lisinopril 10mg"]
    },
    "current_presentations": {
      "chief_complaint": "Persistent anxiety and low mood",
      "symptom_onset": "6 months ago"
    },
    "treatment_history": {
      "prior_therapy": "None",
      "psychiatric_hospitalizations": 0
    },
    "preferences": {
      "therapy_modality_preferences": ["CBT", "Mindfulness"],
      "accessibility_needs": "Telehealth preferred",
      "language": "English"
    }
  }'
```

**Expected Response** (201 Created):
```json
{
  "message": "Patient created successfully",
  "patient": {
    "patient_id": "uuid",
    "clinic_id": "uuid",
    "demographics": { ... },
    "clinical_profile": { ... },
    "created_at": "2024-01-15T10:30:45.123Z"
  }
}
```

**Save patient_id**:
```bash
export PATIENT_ID="your-patient-uuid"
```

### 4B. Create Second Patient (Complex Case)

```bash
curl -X POST http://localhost:3000/api/v1/patients \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "demographics": {
      "first_name": "Michael",
      "last_name": "Johnson",
      "date_of_birth": "1985-03-22",
      "gender": "male",
      "contact_email": "m.johnson@example.com",
      "contact_phone": "+1-217-555-0400"
    },
    "clinical_profile": {
      "dsm5_codes": ["F60.3", "F41.1", "Z62.5"],
      "medical_history": "PTSD from military service, Sleep apnea, Hypertension",
      "current_medications": ["Prazosin 2mg bedtime", "Zolpidem 5mg as needed"]
    },
    "current_presentations": {
      "chief_complaint": "Trauma-related nightmares, hypervigilance, relationship difficulties",
      "symptom_onset": "15 years, recent exacerbation 2 months"
    },
    "treatment_history": {
      "prior_therapy": "EMDR (incomplete), CBT (2 years ago)",
      "psychiatric_hospitalizations": 1,
      "substance_use_history": "Alcohol abuse, 3 years sober"
    },
    "preferences": {
      "therapy_modality_preferences": ["EMDR", "Trauma-focused"],
      "accessibility_needs": "Male therapist preferred",
      "language": "English"
    }
  }'
```

### 4C. Get All Patients

```bash
curl -X GET http://localhost:3000/api/v1/patients \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response** (200 OK):
```json
{
  "count": 2,
  "patients": [ ... ]
}
```

### 4D. Get Patient by ID

```bash
curl -X GET http://localhost:3000/api/v1/patients/$PATIENT_ID \
  -H "Authorization: Bearer $TOKEN"
```

### 4E. Update Patient

```bash
curl -X PUT http://localhost:3000/api/v1/patients/$PATIENT_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_presentations": {
      "chief_complaint": "Anxiety improving with treatment",
      "current_symptoms": "Occasional panic attacks",
      "symptom_onset": "6 months"
    },
    "preferences": {
      "therapy_modality_preferences": ["CBT", "DBT", "Mindfulness"]
    }
  }'
```

---

## Test 5: Clinical Scenario Capture (Flexible Input)

### 5A. Scenario Type: Free Text

**Endpoint**: `POST /api/v1/scenarios`

```bash
curl -X POST http://localhost:3000/api/v1/scenarios \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "'$PATIENT_ID'",
    "scenario_type": "free_text",
    "raw_input": "Patient came in today reporting increased anxiety over the past week. She mentions feeling overwhelmed at work with a new project deadline. Sleep has been disrupted - waking at 3am with racing thoughts. No appetite changes. Denies suicidal ideation. Strong family support system. Previously responded well to CBT techniques.",
    "presenting_problems": ["Anxiety", "Sleep disruption", "Work stress"],
    "dsm5_codes": ["F41.1"],
    "symptom_severity": {
      "anxiety": "7/10",
      "sleep_disruption": "6/10",
      "concentration": "5/10"
    },
    "psychosocial_stressors": {
      "work_stress": true,
      "deadline_pressure": true,
      "marital_conflict": false,
      "financial_stress": false
    },
    "protective_factors": {
      "strong_family_support": true,
      "employment_stability": true,
      "previous_therapy_success": true,
      "exercise_routine": true
    },
    "provider_notes": "Patient is motivated for treatment. Good insight into symptoms. Coping mechanisms somewhat depleted. Recommend active intervention.",
    "urgent_flags": [],
    "session_number": 1
  }'
```

**Expected Response** (201 Created):
```json
{
  "message": "Clinical scenario created successfully",
  "scenario": {
    "scenario_id": "uuid",
    "patient_id": "uuid",
    "therapist_id": "uuid",
    "scenario_type": "free_text",
    "presenting_problems": ["Anxiety", "Sleep disruption", "Work stress"],
    "dsm5_codes": ["F41.1"],
    "symptom_severity": { ... },
    "created_at": "2024-01-15T10:30:45.123Z"
  }
}
```

**Save scenario_id**:
```bash
export SCENARIO_ID="your-scenario-uuid"
```

### 5B. Scenario Type: Structured Form with Assessments

```bash
curl -X POST http://localhost:3000/api/v1/scenarios \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "'$PATIENT_ID'",
    "scenario_type": "structured_form",
    "presenting_problems": ["Depression", "Social withdrawal", "Fatigue"],
    "dsm5_codes": ["F32.9"],
    "symptom_severity": {
      "depressed_mood": "8/10",
      "loss_of_interest": "7/10",
      "fatigue": "8/10",
      "concentration": "6/10",
      "sleep": "5/10"
    },
    "assessment_scales": {
      "phq9": 18,
      "gad7": 12,
      "pcl5": 35
    },
    "psychosocial_stressors": {
      "recent_loss": true,
      "isolation": true,
      "grief": true
    },
    "protective_factors": {
      "supportive_relationships": true,
      "spiritual_practices": true
    },
    "provider_notes": "Moderate to severe depression. Grief-related presentation. Patient not engaging in previously enjoyed activities.",
    "session_number": 3
  }'
```

### 5C. Scenario Type: Chart Review

```bash
curl -X POST http://localhost:3000/api/v1/scenarios \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "'$PATIENT_ID'",
    "scenario_type": "import",
    "presenting_problems": ["PTSD symptoms", "Hypervigilance", "Sleep disturbance"],
    "dsm5_codes": ["F43.10"],
    "assessment_scales": {
      "pcl5": 52,
      "psqi": 18
    },
    "trauma_history": {
      "trauma_type": "Combat exposure",
      "years_since": 15,
      "prior_treatment": "EMDR",
      "treatment_response": "partial"
    },
    "substance_use": {
      "alcohol": "Previously heavy use, now abstinent 3 years",
      "current_use": "None"
    },
    "provider_notes": "Chart imported from VA records. Recent exacerbation of symptoms post-anniversary of deployment.",
    "urgent_flags": ["nightmares", "hypervigilance"],
    "session_number": 2
  }'
```

### 5D. Scenario Type: Transcription

```bash
curl -X POST http://localhost:3000/api/v1/scenarios \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "'$PATIENT_ID'",
    "scenario_type": "transcription",
    "raw_input": "[Session transcript summary] Patient discussed recent panic attack in grocery store. Felt trapped, chest tightness, heart racing. Used grounding techniques discussed in prior session - helped some. Expressed frustration with limitations to activities. Therapist explored avoidance patterns. Identified trigger: crowded spaces with no easy exit. Discussed exposure hierarchy for next session.",
    "presenting_problems": ["Panic attacks", "Agoraphobia", "Avoidance"],
    "dsm5_codes": ["F40.01"],
    "assessment_scales": {
      "gad7": 16,
      "pas": 28
    },
    "provider_notes": "Good progress with grounding techniques. Ready for graduated exposure work.",
    "session_number": 4
  }'
```

### 5E. Get Scenario

```bash
curl -X GET http://localhost:3000/api/v1/scenarios/$SCENARIO_ID \
  -H "Authorization: Bearer $TOKEN"
```

### 5F. Get All Scenarios for Patient

```bash
curl -X GET http://localhost:3000/api/v1/scenarios/patient/$PATIENT_ID \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response** (200 OK):
```json
{
  "count": 4,
  "scenarios": [
    { ... scenario 1 ... },
    { ... scenario 2 ... },
    { ... scenario 3 ... },
    { ... scenario 4 ... }
  ]
}
```

### 5G. Update Scenario

```bash
curl -X PUT http://localhost:3000/api/v1/scenarios/$SCENARIO_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "assessment_scales": {
      "phq9": 14,
      "gad7": 12
    },
    "provider_notes": "Patient showing improvement with current intervention. Continue current approach."
  }'
```

---

## Test 6: Therapy Modalities Reference Data

### 6A. Verify Therapy Modalities Were Seeded

```bash
psql -U postgres -d smart_communicator -c "SELECT COUNT(*) FROM therapy_modalities;"
```

**Expected**: Count should be 13

### 6B. List Therapy Modalities

```bash
psql -U postgres -d smart_communicator -c "SELECT modality_id, name, abbreviation, category FROM therapy_modalities LIMIT 5;"
```

**Expected**: Should see modalities like CBT, DBT, ACT, etc.

### 6C. Check Modality Combinations

```bash
psql -U postgres -d smart_communicator -c "SELECT * FROM modality_combinations LIMIT 5;"
```

**Expected**: Should see integration rules between modalities

---

## Test 7: Error Handling & Validation

### 7A. Missing Required Field

```bash
curl -X POST http://localhost:3000/api/v1/patients \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "demographics": {
      "first_name": "Test"
    }
  }'
```

**Expected Response** (400 Bad Request):
```json
{
  "error": "description of validation error"
}
```

### 7B. Invalid Data Type

```bash
curl -X POST http://localhost:3000/api/v1/scenarios \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "'$PATIENT_ID'",
    "scenario_type": "invalid_type",
    "raw_input": "test"
  }'
```

**Expected Response** (400 Bad Request):
```json
{
  "error": "Must be one of: free_text, structured_form, import, transcription"
}
```

### 7C. Invalid Token

```bash
curl -X GET http://localhost:3000/api/v1/patients \
  -H "Authorization: Bearer invalid-token"
```

**Expected Response** (403 Forbidden):
```json
{
  "error": "Invalid or expired token"
}
```

### 7D. Not Found

```bash
curl -X GET http://localhost:3000/api/v1/patients/nonexistent-uuid \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response** (404 Not Found):
```json
{
  "error": "Patient not found"
}
```

### 7E. Duplicate Email Registration

```bash
curl -X POST http://localhost:3000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dr.smith@clinic.com",
    "password": "AnotherPassword123!",
    "first_name": "John",
    "last_name": "Smith"
  }'
```

**Expected Response** (409 Conflict):
```json
{
  "error": "Therapist with this email already exists"
}
```

---

## Test 8: Assessment Scale Verification

### 8A. Check Assessment Scale Data Integrity

```bash
psql -U postgres -d smart_communicator << 'EOF'
SELECT
  assessment_scales,
  (assessment_scales::jsonb ->> 'phq9')::int as phq9,
  (assessment_scales::jsonb ->> 'gad7')::int as gad7,
  (assessment_scales::jsonb ->> 'pcl5')::int as pcl5
FROM clinical_scenarios
WHERE assessment_scales IS NOT NULL
LIMIT 3;
EOF
```

**Expected**: Should show assessment scale values properly stored

### 8B. Verify Symptom Severity Storage

```bash
psql -U postgres -d smart_communicator << 'EOF'
SELECT
  scenario_id,
  symptom_severity,
  (symptom_severity::jsonb ->> 'anxiety') as anxiety_level
FROM clinical_scenarios
WHERE symptom_severity IS NOT NULL
LIMIT 1;
EOF
```

---

## Test 9: Data Relationships

### 9A. Verify Therapist-Clinic Association

```bash
psql -U postgres -d smart_communicator << 'EOF'
SELECT t.therapist_id, t.email, c.name
FROM therapists t
INNER JOIN clinics c ON t.clinic_id = c.clinic_id
LIMIT 1;
EOF
```

### 9B. Verify Patient-Clinic Association

```bash
psql -U postgres -d smart_communicator << 'EOF'
SELECT p.patient_id, p.demographics::jsonb ->> 'first_name' as name,
       c.name as clinic_name
FROM unified_patient_profiles p
INNER JOIN clinics c ON p.clinic_id = c.clinic_id
LIMIT 1;
EOF
```

### 9C. Verify Scenario-Patient-Therapist Chain

```bash
psql -U postgres -d smart_communicator << 'EOF'
SELECT
  s.scenario_id,
  s.presenting_problems,
  p.demographics::jsonb ->> 'first_name' as patient_name,
  t.email as therapist_email
FROM clinical_scenarios s
INNER JOIN unified_patient_profiles p ON s.patient_id = p.patient_id
INNER JOIN therapists t ON s.therapist_id = t.therapist_id
LIMIT 1;
EOF
```

---

## Test 10: Performance Check

### 10A. Response Time for List Endpoints

```bash
time curl -X GET http://localhost:3000/api/v1/patients \
  -H "Authorization: Bearer $TOKEN" \
  -s | jq .
```

**Expected**: Response time < 200ms for small datasets

### 10B. Query Large Scenario List

```bash
curl -X GET "http://localhost:3000/api/v1/scenarios/patient/$PATIENT_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -s | jq '.count'
```

---

## Summary Checklist

- [ ] Health check endpoint responds
- [ ] Therapist registration works
- [ ] Therapist login works
- [ ] Token-based authentication works
- [ ] Invalid credentials rejected
- [ ] Missing token rejected
- [ ] Clinic creation works
- [ ] Clinic retrieval works
- [ ] Clinic updates work
- [ ] Patient creation works
- [ ] Patient retrieval works
- [ ] Patient updates work
- [ ] Scenario creation with free text works
- [ ] Scenario creation with structured form works
- [ ] Scenario creation with assessments works
- [ ] Scenario retrieval works
- [ ] Scenario updates work
- [ ] Assessment scales stored correctly
- [ ] Symptom severity stored correctly
- [ ] Error validation works (400)
- [ ] Authentication errors work (401/403)
- [ ] Not found errors work (404)
- [ ] Conflict errors work (409)
- [ ] Database relationships intact
- [ ] Response times acceptable

## Known Issues & Refinements Needed

Track any issues found during testing here.

---

## Next Steps After Testing

1. Fix any identified issues
2. Optimize slow queries if needed
3. Add additional validation if edge cases found
4. Move to Phase 2: ML recommendations
