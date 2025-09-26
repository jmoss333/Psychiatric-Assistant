# Backend

This is a simple Express server providing placeholder endpoints for the three modules:
- `/api/group-therapy`
- `/api/intervention`
- `/api/aftercare`

## Setup

Copy `.env.example` to `.env` and add your Supabase credentials.

Run with:
```bash
npm install
node app.js
```

## Database Setup and Analytics

1. **Create the Schema**

   Use the SQL file in `../db/schema.sql` to set up your database tables:

   ```bash
   psql "$DB_CONNECTION_STRING" -f ../db/schema.sql
   ```

2. **Configure Environment Variables**

   Create a `.env` file in this directory containing your connection details. The scripts expect variables such as `DB_CONNECTION_STRING`, `SUPABASE_URL`, and `SUPABASE_SERVICE_KEY`.

3. **Seed the Database**

   Populate initial data using the provided seeding script:

   ```bash
   node seedSupabase.js
   ```

4. **Run Analytics**

   After seeding, execute the analytics script to generate reports:

   ```bash
   node analytics.js
   ```

### Order of Operations

Run the steps above in sequence: first create the schema, then seed the database, and finally run the analytics script.
