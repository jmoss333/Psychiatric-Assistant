# Smart Communicator API Documentation

## Overview
The Smart Communicator API provides endpoints for managing therapists, patients, clinics, and clinical decision support for therapy guidance. This is Phase 1 of the implementation focusing on authentication, patient intake, and clinical scenario capture.

## Base URL
```
http://localhost:3000/api/v1
```

## Authentication
Most endpoints require JWT token authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Endpoints

### Authentication (Public)

#### Register a Therapist
```
POST /auth/register
Content-Type: application/json

{
  "email": "therapist@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe"
}

Response: 201 Created
{
  "message": "Therapist registered successfully",
  "token": "eyJhbGc...",
  "therapist": {
    "therapist_id": "uuid",
    "email": "therapist@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

#### Login
```
POST /auth/login
Content-Type: application/json

{
  "email": "therapist@example.com",
  "password": "securepassword123"
}

Response: 200 OK
{
  "message": "Login successful",
  "token": "eyJhbGc...",
  "therapist": {
    "therapist_id": "uuid",
    "email": "therapist@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

#### Logout
```
POST /auth/logout

Response: 200 OK
{
  "message": "Logout successful"
}
```

---

### Clinic Management

#### Create Clinic
```
POST /clinics
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Urban Mental Health Clinic",
  "address": {
    "street": "123 Main St",
    "city": "Springfield",
    "state": "IL",
    "zip": "62701",
    "country": "USA"
  },
  "phone": "+1-217-555-0100",
  "email": "contact@clinic.com",
  "license_number": "IL123456"
}

Response: 201 Created
{
  "message": "Clinic created successfully",
  "clinic": {
    "clinic_id": "uuid",
    "name": "Urban Mental Health Clinic",
    ...
  }
}
```

#### Get My Clinics
```
GET /clinics
Authorization: Bearer <token>

Response: 200 OK
{
  "clinics": [
    {
      "clinic_id": "uuid",
      "name": "Urban Mental Health Clinic",
      ...
    }
  ]
}
```

#### Get Clinic by ID
```
GET /clinics/{clinic_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "clinic": {
    "clinic_id": "uuid",
    "name": "Urban Mental Health Clinic",
    ...
  }
}
```

#### Update Clinic
```
PUT /clinics/{clinic_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated Clinic Name",
  "phone": "+1-217-555-0101",
  "status": "active"
}

Response: 200 OK
{
  "message": "Clinic updated successfully",
  "clinic": { ... }
}
```

---

### Patient Management

#### Create Patient (Intake)
```
POST /patients
Authorization: Bearer <token>
Content-Type: application/json

{
  "demographics": {
    "first_name": "Jane",
    "last_name": "Smith",
    "date_of_birth": "1990-05-15",
    "gender": "female",
    "contact_email": "jane@example.com",
    "contact_phone": "+1-217-555-0200"
  },
  "clinical_profile": {
    "dsm5_codes": ["F41.1", "F32.9"],
    "medical_history": "Type 2 Diabetes, Hypertension",
    "current_medications": ["Sertraline 50mg daily", "Lisinopril 10mg daily"]
  },
  "current_presentations": {
    "chief_complaint": "Persistent anxiety and low mood",
    "symptom_duration": "6 months"
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
}

Response: 201 Created
{
  "message": "Patient created successfully",
  "patient": {
    "patient_id": "uuid",
    "clinic_id": "uuid",
    "demographics": { ... },
    "clinical_profile": { ... }
  }
}
```

#### Get All Patients
```
GET /patients
Authorization: Bearer <token>

Response: 200 OK
{
  "count": 1,
  "patients": [ ... ]
}
```

#### Get Patient by ID
```
GET /patients/{patient_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "patient": {
    "patient_id": "uuid",
    "demographics": { ... },
    "clinical_profile": { ... }
  }
}
```

#### Update Patient
```
PUT /patients/{patient_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "current_presentations": {
    "chief_complaint": "Anxiety improving with treatment",
    "symptom_duration": "6 months"
  },
  "preferences": {
    "therapy_modality_preferences": ["CBT", "DBT"]
  }
}

Response: 200 OK
{
  "message": "Patient updated successfully",
  "patient": { ... }
}
```

#### Get Patient's Scenarios
```
GET /patients/{patient_id}/scenarios
Authorization: Bearer <token>

Response: 200 OK
{
  "count": 2,
  "scenarios": [ ... ]
}
```

---

### Clinical Scenarios (Flexible Input)

#### Create Clinical Scenario
```
POST /scenarios
Authorization: Bearer <token>
Content-Type: application/json

{
  "patient_id": "uuid",
  "scenario_type": "free_text",
  "raw_input": "Patient came in today expressing increased anxiety. Reports sleep disruption and difficulty concentrating. Mentioned recent conflict with spouse.",
  "presenting_problems": ["Anxiety", "Sleep disruption", "Concentration difficulty"],
  "dsm5_codes": ["F41.1"],
  "symptom_severity": {
    "anxiety": "7/10",
    "sleep_disruption": "6/10",
    "concentration": "5/10"
  },
  "psychosocial_stressors": {
    "marital_conflict": true,
    "work_stress": false
  },
  "protective_factors": {
    "strong_family_support": true,
    "employment_stability": true
  },
  "assessment_scales": {
    "phq9": 14,
    "gad7": 16
  },
  "provider_notes": "Patient is motivated for treatment. Good insight into symptoms.",
  "urgent_flags": [],
  "session_number": 1
}

Response: 201 Created
{
  "message": "Clinical scenario created successfully",
  "scenario": {
    "scenario_id": "uuid",
    "patient_id": "uuid",
    "therapist_id": "uuid",
    "presenting_problems": [ ... ],
    "dsm5_codes": [ ... ]
  }
}
```

#### Get Scenario by ID
```
GET /scenarios/{scenario_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "scenario": {
    "scenario_id": "uuid",
    "patient_id": "uuid",
    "presenting_problems": [ ... ],
    "assessment_scales": { ... }
  }
}
```

#### Update Scenario
```
PUT /scenarios/{scenario_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "assessment_scales": {
    "phq9": 12,
    "gad7": 14
  },
  "provider_notes": "Patient showing improvement. Recommending continued current approach."
}

Response: 200 OK
{
  "message": "Scenario updated successfully",
  "scenario": { ... }
}
```

#### Get All Scenarios for a Patient
```
GET /scenarios/patient/{patient_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "count": 3,
  "scenarios": [ ... ]
}
```

---

## Error Responses

### 401 Unauthorized
```json
{
  "error": "Access token required"
}
```

### 403 Forbidden
```json
{
  "error": "Invalid or expired token"
}
```

### 404 Not Found
```json
{
  "error": "Patient not found"
}
```

### 409 Conflict
```json
{
  "error": "Therapist with this email already exists"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

---

## Setup Instructions

### Prerequisites
- Node.js 14+
- PostgreSQL 12+

### Installation
```bash
cd backend
npm install
```

### Configuration
1. Create `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

2. Update database credentials in `.env`:
```
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your-password
DB_NAME=smart_communicator
```

### Database Setup
1. Create database:
```bash
createdb smart_communicator
```

2. Run schema:
```bash
psql -U postgres -d smart_communicator -f ../db/schema.sql
```

### Running the Server
```bash
# Development
npm run dev

# Production
npm start
```

The API will be available at `http://localhost:3000/api/v1`

---

## Next Steps (Phase 2)
- ML-powered modality recommendations
- Session tracking and outcome recording
- Real-time guidance engine
- Mobile app integration
- Web dashboard for therapists
