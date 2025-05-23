# Setup Instructions

This project is a basic prototype. To run the backend API:

```bash
cd backend
npm install # requires internet access to fetch dependencies
node app.js
```

Environment variables required for Supabase:
```
SUPABASE_URL=<your supabase project URL>
SUPABASE_KEY=<service role key>
```

Seed example data:
```
node intervention-seeder.js
```

Generate an analytics report:
```
npm run analytics
```

The mobile app requires React Native CLI or Expo. The web dashboard is a simple static page.

Due to environment constraints, dependencies are not installed in this repository.
