# Backend

This is a simple Express server providing placeholder endpoints for the three modules:
- `/api/group-therapy`
- `/api/intervention`
- `/api/aftercare`

Run with:
```bash
npm install
node app.js
```

## Seeding Sample Data

A script is provided to seed 20 sample intervention records in Supabase. Copy `.env.example` to `.env` and fill in your project credentials:

```bash
cp .env.example .env
# edit .env with your SUPABASE_URL and SUPABASE_SERVICE_KEY
```

Install dependencies if you haven't already, then run:

```bash
npm install
node seed-data.js
```

This will ensure the patient and provider records exist and insert sample interventions referencing them.
