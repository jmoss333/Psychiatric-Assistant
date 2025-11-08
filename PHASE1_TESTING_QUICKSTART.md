# Phase 1 Testing Quick Start Guide

Complete walkthrough for testing the Smart Communicator Phase 1 backend implementation.

## 5-Minute Setup

### 1. Prepare Database (2 min)

```bash
# Create database
createdb smart_communicator

# Navigate to project
cd Smart-Communicator

# Load schema
psql -U postgres -d smart_communicator -f db/schema.sql

# Seed reference data (therapy modalities, etc.)
psql -U postgres -d smart_communicator -f db/seed.sql

# Verify setup
./backend/verify-db.sh
```

Expected output: "✓ Database is ready for testing"

### 2. Install & Start Backend (3 min)

```bash
cd backend

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Start development server
npm run dev
```

Expected output:
```
Smart Communicator Backend listening on port 3000
Environment: development
API Documentation: http://localhost:3000/api/v1
```

## Testing Options

### Option A: Automated Tests (Recommended)

Run all tests automatically:

```bash
node test-runner.js
```

This will:
- Test health check
- Register & login therapists
- Test clinic management
- Test patient intake
- Test clinical scenarios (all input types)
- Test error handling
- Print comprehensive report

Expected: 30+ tests, 90%+ pass rate

### Option B: Manual Testing with Curl

Follow the detailed TESTING.md guide with curl commands.

### Option C: Interactive Testing

Test individual endpoints one at a time using curl:

```bash
# 1. Health check
curl http://localhost:3000/health

# 2. Register therapist (save token)
TOKEN=$(curl -s -X POST http://localhost:3000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@clinic.com",
    "password": "TestPassword123!",
    "first_name": "John",
    "last_name": "Doe"
  }' | jq -r '.token')

echo "Token: $TOKEN"

# 3. Create clinic
CLINIC=$(curl -s -X POST http://localhost:3000/api/v1/clinics \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Clinic",
    "phone": "+1-555-0100",
    "email": "contact@clinic.com"
  }')

CLINIC_ID=$(echo $CLINIC | jq -r '.clinic.clinic_id')
echo "Clinic ID: $CLINIC_ID"

# 4. Create patient
PATIENT=$(curl -s -X POST http://localhost:3000/api/v1/patients \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "demographics": {
      "first_name": "Jane",
      "last_name": "Patient",
      "date_of_birth": "1990-05-15",
      "gender": "female"
    },
    "clinical_profile": {
      "dsm5_codes": ["F41.1"],
      "medical_history": "Anxiety disorder"
    }
  }')

PATIENT_ID=$(echo $PATIENT | jq -r '.patient.patient_id')
echo "Patient ID: $PATIENT_ID"

# 5. Create clinical scenario
SCENARIO=$(curl -s -X POST http://localhost:3000/api/v1/scenarios \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "'$PATIENT_ID'",
    "scenario_type": "free_text",
    "raw_input": "Patient reports increased anxiety and sleep disruption.",
    "presenting_problems": ["Anxiety", "Sleep disruption"],
    "dsm5_codes": ["F41.1"],
    "assessment_scales": {
      "phq9": 14,
      "gad7": 16
    }
  }')

SCENARIO_ID=$(echo $SCENARIO | jq -r '.scenario.scenario_id')
echo "Scenario ID: $SCENARIO_ID"

# 6. Retrieve created data
curl -s http://localhost:3000/api/v1/scenarios/$SCENARIO_ID \
  -H "Authorization: Bearer $TOKEN" | jq .
```

## Test Coverage

### ✓ Core Features Tested

- **Authentication**: Register, login, token validation
- **Clinic Management**: Create, read, update clinics
- **Patient Management**: Intake, CRUD operations
- **Clinical Scenarios**: Flexible input (free text, structured, import, transcription)
- **Assessment Scales**: PHQ-9, GAD-7, PCL-5 storage and retrieval
- **Error Handling**: Validation, authentication, not found, conflicts
- **Data Integrity**: Relationships, JSONB storage, indexing

### ✓ Endpoints Tested (25+ endpoints)

**Authentication** (3):
- POST /auth/register
- POST /auth/login
- POST /auth/logout

**Clinics** (4):
- POST /clinics
- GET /clinics
- GET /clinics/{id}
- PUT /clinics/{id}

**Patients** (5):
- POST /patients
- GET /patients
- GET /patients/{id}
- PUT /patients/{id}
- GET /patients/{id}/scenarios

**Scenarios** (4):
- POST /scenarios
- GET /scenarios/{id}
- PUT /scenarios/{id}
- GET /scenarios/patient/{id}

**Health** (1):
- GET /health

## Expected Test Results

### Successful Test Run
```
✓ Passed: 31
✗ Failed: 0
Total: 31

Pass Rate: 100%
```

### Common Issues & Solutions

#### "Database does not exist"
```bash
createdb smart_communicator
psql -U postgres -d smart_communicator -f db/schema.sql
psql -U postgres -d smart_communicator -f db/seed.sql
```

#### "Connection refused" (can't connect to server)
- Check if backend is running: `npm run dev`
- Check port 3000 is available: `lsof -i :3000`

#### "Token invalid or expired"
- Tokens expire after 24 hours
- Register new therapist or use login to get fresh token

#### "Validation error"
- Check required fields in request body
- Refer to API_DOCUMENTATION.md for field requirements

#### "Clinic/Patient not found"
- Ensure you created clinic/patient first
- Use correct UUIDs (copy from creation response)

## Verification Checklist

After running tests, verify:

- [ ] 31+ tests pass
- [ ] Database has 13 therapy modalities
- [ ] Can register and login therapists
- [ ] Can create multiple clinics
- [ ] Can create patients with full demographics
- [ ] Can create clinical scenarios with assessments
- [ ] Scenario data persists (can retrieve after create)
- [ ] Assessment scales (PHQ-9, GAD-7) stored correctly
- [ ] Error responses are consistent
- [ ] Invalid tokens are rejected
- [ ] CORS headers present
- [ ] Response times < 200ms

## Database Inspection

Verify data was created correctly:

```bash
# Check therapy modalities
psql -U postgres -d smart_communicator -c \
  "SELECT name, abbreviation, category FROM therapy_modalities LIMIT 5;"

# Check created therapist
psql -U postgres -d smart_communicator -c \
  "SELECT therapist_id, email, first_name FROM therapists;"

# Check created patient
psql -U postgres -d smart_communicator -c \
  "SELECT patient_id, demographics FROM unified_patient_profiles;"

# Check clinical scenario with assessments
psql -U postgres -d smart_communicator -c \
  "SELECT scenario_id, presenting_problems, assessment_scales FROM clinical_scenarios;"
```

## Next Steps

### After Successful Testing

1. **Review Test Results**: Check test-runner output for any warnings
2. **Check Database**: Run verify-db.sh to confirm data integrity
3. **Review Logs**: Check server logs for any errors
4. **Move to Phase 2**: Start ML recommendation engine implementation

### If Issues Found

1. **Isolate Problem**: Run individual test or use manual curl testing
2. **Check Logs**: Look at backend server output for error details
3. **Review Code**: Check relevant route file (routes/*.js)
4. **Verify Data**: Use psql to inspect database state
5. **Document Issue**: Add to ISSUES.md for later fixes

## Performance Baseline

Record these baseline numbers for Phase 2 comparison:

```bash
# Run this after successful test
echo "=== Performance Baseline ==="
time node test-runner.js
echo "=== Database Size ==="
psql -U postgres -d smart_communicator -c \
  "SELECT pg_size_pretty(pg_database_size('smart_communicator'));"
```

## Troubleshooting Commands

```bash
# Reset everything (careful!)
dropdb smart_communicator
createdb smart_communicator
psql -U postgres -d smart_communicator -f db/schema.sql
psql -U postgres -d smart_communicator -f db/seed.sql

# Clear test data (keep modalities)
psql -U postgres -d smart_communicator -c \
  "DELETE FROM clinical_scenarios; DELETE FROM therapy_sessions; DELETE FROM unified_patient_profiles; DELETE FROM therapists; DELETE FROM clinics;"

# Check server is running
curl http://localhost:3000/health

# View recent logs
tail -f /tmp/smart-communicator.log

# Kill server if stuck
pkill -f "npm run dev"
```

## File References

- **Backend Code**: `/backend/routes/` - All endpoint implementations
- **Schema**: `/db/schema.sql` - Database structure
- **Seed Data**: `/db/seed.sql` - Reference data (13 modalities)
- **API Docs**: `/backend/API_DOCUMENTATION.md` - Detailed endpoint specs
- **Full Tests**: `/backend/TESTING.md` - Comprehensive testing guide
- **Config**: `/backend/.env.example` - Environment configuration

## Success Criteria

✅ Phase 1 testing is successful when:

1. All automated tests pass (>90% pass rate)
2. Database schema is complete with all 13 tables
3. Can register and login therapists
4. Can create clinics and patients
5. Can capture clinical scenarios with flexible input
6. Assessment scales properly stored
7. Error handling returns correct status codes
8. No obvious performance issues
9. Data persists across server restarts
10. Ready to proceed to Phase 2 (ML recommendations)

## Documentation

For detailed information:
- Backend features: `/backend/README.md`
- API endpoints: `/backend/API_DOCUMENTATION.md`
- Full testing guide: `/backend/TESTING.md`
- Database schema: `/db/schema.sql`

---

**Estimated Time**: 20 minutes (setup + automated tests)
**Expected Result**: 31+ passing tests, 100% pass rate
**Next Phase**: ML-powered therapy recommendations (Phase 2)
