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

## Environment Variables
Create a `.env` file in this directory based on `.env.example` and provide your Supabase credentials.

## Seeding Sample Data
The `seedSupabase.js` script inserts example interventions into a Supabase database. After creating the `.env` file, run:
```bash
node seedSupabase.js
```

## Running Analytics
`analytics.js` reports counts and averages for the interventions table:
```bash
node analytics.js
```
