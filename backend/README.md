# Smart Communicator Backend

A clinical decision support system API for therapists, providing real-time guidance on therapy modality selection and technique recommendations.

## Features

- **Therapist Authentication**: Secure JWT-based authentication for therapists
- **Clinic Management**: Multi-clinic support with therapist-clinic associations
- **Patient Management**: Comprehensive patient intake and profile management
- **Flexible Clinical Scenario Capture**: Support for multiple input types (free text, structured forms, chart reviews, transcripts)
- **Database Schema**: PostgreSQL with JSONB for flexible clinical data storage
- **Assessment Scales Integration**: Support for standard assessment tools (PHQ-9, GAD-7, PCL-5, etc.)
- **Outcome Tracking Foundation**: Ready for outcome measurement and feedback loops

## Technology Stack

- **Runtime**: Node.js 14+
- **Framework**: Express.js 4.18.2
- **Database**: PostgreSQL 12+ with pgvector support
- **Authentication**: JWT (jsonwebtoken)
- **Password Security**: bcryptjs
- **Validation**: Joi
- **Middleware**: Helmet (security), CORS
- **Environment**: dotenv

## Project Structure

```
backend/
├── routes/              # Express route handlers
│   ├── auth.js         # Therapist authentication (register, login)
│   ├── clinics.js      # Clinic management
│   ├── patients.js     # Patient intake and profiles
│   └── scenarios.js    # Clinical scenario capture
├── middleware/
│   └── auth.js         # JWT authentication middleware
├── utils/
│   └── validators.js   # Input validation (Joi schemas)
├── db/
│   └── config.js       # Database connection pooling
├── app.js              # Main application file
├── package.json        # Dependencies
├── .env.example        # Environment variables template
├── API_DOCUMENTATION.md # Complete API reference
└── README.md          # This file
```

## Quick Start

### Prerequisites
- Node.js 14 or higher
- PostgreSQL 12 or higher
- npm or yarn

### Installation

1. **Install dependencies**:
```bash
cd backend
npm install
```

2. **Set up environment variables**:
```bash
cp .env.example .env
```

Edit `.env` with your database credentials:
```
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=smart_communicator
JWT_SECRET=your-super-secret-key-change-in-production
```

3. **Create database**:
```bash
createdb smart_communicator
```

4. **Run database schema**:
```bash
psql -U postgres -d smart_communicator -f ../db/schema.sql
```

5. **Seed reference data** (therapy modalities, etc.):
```bash
psql -U postgres -d smart_communicator -f ../db/seed.sql
```

### Running the Server

**Development mode** (with auto-restart):
```bash
npm run dev
```

**Production mode**:
```bash
npm start
```

The API will be available at `http://localhost:3000/api/v1`

Health check: `http://localhost:3000/health`

## API Overview

### Public Endpoints (Authentication)
- `POST /api/v1/auth/register` - Register new therapist
- `POST /api/v1/auth/login` - Login therapist
- `POST /api/v1/auth/logout` - Logout

### Protected Endpoints (Require JWT Token)

**Clinics**:
- `POST /api/v1/clinics` - Create clinic
- `GET /api/v1/clinics` - Get my clinics
- `GET /api/v1/clinics/{clinic_id}` - Get clinic details
- `PUT /api/v1/clinics/{clinic_id}` - Update clinic

**Patients**:
- `POST /api/v1/patients` - Create patient (intake)
- `GET /api/v1/patients` - List my patients
- `GET /api/v1/patients/{patient_id}` - Get patient details
- `PUT /api/v1/patients/{patient_id}` - Update patient
- `GET /api/v1/patients/{patient_id}/scenarios` - Get patient's clinical scenarios

**Clinical Scenarios**:
- `POST /api/v1/scenarios` - Create clinical scenario
- `GET /api/v1/scenarios/{scenario_id}` - Get scenario details
- `PUT /api/v1/scenarios/{scenario_id}` - Update scenario
- `GET /api/v1/scenarios/patient/{patient_id}` - Get all scenarios for patient

See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for detailed specifications and examples.

## Database Setup

### Create Database
```bash
createdb smart_communicator
```

### Run Schema
```bash
psql -U postgres -d smart_communicator -f ../db/schema.sql
```

### Seed Reference Data
```bash
psql -U postgres -d smart_communicator -f ../db/seed.sql
```

This creates therapy modality reference data, modality combinations, and base clinic.

## Database Schema

Core tables supporting clinical decision support:

- **clinics**: Clinic information and settings
- **therapists**: Therapist profiles with credentials and expertise
- **unified_patient_profiles**: Unified patient demographics and clinical info
- **therapy_modalities**: Reference data for 15+ therapy modalities
- **modality_combinations**: Evidence-based modality integration rules
- **clinical_scenarios**: Flexible storage for clinical scenario data (free text, structured assessments)
- **recommendations**: ML-powered therapy recommendations (Phase 2)
- **therapy_sessions**: Session execution and tracking
- **session_outcomes**: Short/medium/long-term outcome tracking
- **long_term_outcomes**: 6-month follow-up and effectiveness data
- **integrated_analytics**: Cross-clinic analytics and correlations

See [../db/schema.sql](../db/schema.sql) for complete schema definitions.

## Authentication Flow

1. **Register**: `POST /auth/register` with email and password
2. **Login**: `POST /auth/login` returns JWT token
3. **Use Token**: Include `Authorization: Bearer <token>` in subsequent requests
4. **Token Expiry**: Tokens expire after 24 hours

## Clinical Scenario Input Types

The system supports flexible input for clinical scenarios:

- **Free Text**: Unstructured therapist notes
- **Structured Form**: Predefined clinical assessment forms
- **Chart Import**: Data imported from EHR systems
- **Transcription**: Session recording transcripts

All types support optional structured data like DSM-5 codes, assessment scales, and symptom ratings.

## Security Considerations

- Passwords hashed with bcryptjs (10 rounds)
- JWT tokens with 24-hour expiration
- Helmet.js for HTTP header security
- CORS configured for allowed origins
- Input validation on all endpoints (Joi)
- SQL injection prevention via parameterized queries
- No sensitive data logged
- Environment variables for secrets (never hardcoded)

## Error Handling

Consistent error responses with HTTP status codes:

- `200 OK` - Request successful
- `201 Created` - Resource created
- `400 Bad Request` - Invalid input/validation error
- `401 Unauthorized` - Missing/invalid token
- `403 Forbidden` - Valid token but not authorized
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource already exists
- `500 Internal Server Error` - Server error

Error response format:
```json
{
  "error": "Descriptive error message"
}
```

## Testing the API

### 1. Register
```bash
curl -X POST http://localhost:3000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "therapist@example.com",
    "password": "securepassword123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:3000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "therapist@example.com",
    "password": "securepassword123"
  }'
```

Copy the returned token for subsequent requests.

### 3. Create Patient
```bash
curl -X POST http://localhost:3000/api/v1/patients \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "demographics": {
      "first_name": "Jane",
      "last_name": "Smith",
      "date_of_birth": "1990-05-15",
      "gender": "female"
    },
    "clinical_profile": {
      "dsm5_codes": ["F41.1"],
      "medical_history": "Type 2 Diabetes"
    }
  }'
```

### 4. Create Clinical Scenario
```bash
curl -X POST http://localhost:3000/api/v1/scenarios \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "PATIENT_UUID",
    "scenario_type": "free_text",
    "raw_input": "Patient reports increased anxiety and sleep disruption...",
    "presenting_problems": ["Anxiety", "Sleep disruption"],
    "dsm5_codes": ["F41.1"],
    "assessment_scales": {
      "phq9": 14,
      "gad7": 16
    }
  }'
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | localhost | PostgreSQL host |
| `DB_PORT` | 5432 | PostgreSQL port |
| `DB_USER` | postgres | PostgreSQL user |
| `DB_PASSWORD` | postgres | PostgreSQL password |
| `DB_NAME` | smart_communicator | Database name |
| `PORT` | 3000 | Express server port |
| `NODE_ENV` | development | Environment mode |
| `JWT_SECRET` | your-secret-key | JWT signing secret (CHANGE IN PRODUCTION!) |
| `CORS_ORIGIN` | localhost:3000 | Allowed CORS origins |

## Troubleshooting

### PostgreSQL Connection Issues
```bash
# Check if PostgreSQL is running
pg_isready -h localhost

# Start PostgreSQL
# macOS: brew services start postgresql
# Linux: sudo systemctl start postgresql
# Windows: net start postgresql-x64-VERSION
```

### Database Not Found
```bash
# Create database
createdb smart_communicator

# Verify
psql -l | grep smart_communicator
```

### Schema Not Applied
```bash
# Run schema
psql -U postgres -d smart_communicator -f ../db/schema.sql

# Verify
psql -U postgres -d smart_communicator -c "\dt"
```

### Port Already in Use
Change `PORT` in `.env` or kill process:
```bash
# Find process on port 3000
lsof -i :3000

# Kill process
kill -9 PID
```

## Phase 1 Completion

✅ **Implemented**:
- Express backend with modular routes
- JWT authentication and authorization
- Clinic management system
- Patient intake and profile management
- Flexible clinical scenario capture
- Database schema with JSONB support
- Input validation with Joi
- Security middleware (Helmet, CORS)
- Error handling
- API documentation
- Complete README and setup instructions

⏳ **Phase 2 (Upcoming)**:
- ML-powered therapy modality recommendations
- Session tracking and outcome recording
- Recommendation accuracy feedback loop
- Integrated therapy suggestions
- Real-time clinical guidance engine
- Web dashboard for therapists
- Mobile app integration

## Contributing

When adding new endpoints:
1. Add validation schema to `utils/validators.js`
2. Create/update route in `routes/`
3. Add `authenticateToken` middleware for protected endpoints
4. Document in `API_DOCUMENTATION.md`
5. Test with provided curl examples

## Support

Refer to:
- [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) - Detailed endpoint specs
- [../db/schema.sql](../db/schema.sql) - Database schema
- [../db/seed.sql](../db/seed.sql) - Reference data

For issues, check troubleshooting section above or refer to project documentation.
