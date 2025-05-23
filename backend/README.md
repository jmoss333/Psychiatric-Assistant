# Backend

This Express server exposes API routes for the project.

Routes:
- `/api/group-therapy` – placeholder
- `/api/interventions/quick-log` – create a quick intervention log
- `/api/interventions/recent` – last 10 interventions
- `/api/aftercare` – placeholder

Run with:
```bash
npm install
node app.js
```

Seed sample patients and providers:
```bash
node intervention-seeder.js
```

Generate an analytics report:
```bash
npm run analytics
```

`services/evidence-service.js` provides a helper to fetch clinical evidence from
Gemini and OpenEvidence. Results are cached in `openEvidence-cache.json`.
