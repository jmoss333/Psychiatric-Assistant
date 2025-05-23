# Setup Instructions

This project is a basic prototype. To run the backend API:

```bash
cd backend
npm install # requires internet access to fetch dependencies
node app.js
```

The mobile app requires React Native CLI or Expo. The web dashboard is a simple static page.

Due to environment constraints, dependencies are not installed in this repository.

## Seeding the Database

To add sample intervention data to your Supabase project, first configure the environment variables in `backend/.env` (see `backend/.env.example`). Then run the seeding script:

```bash
cd backend
npm install
node seed-data.js
```

This creates a test patient and provider (if they don't already exist) and inserts 20 intervention records linked to them.
