const express = require('express');
const app = express();
app.use(express.json());

// API routes
const interventionRoutes = require('./routes/interventions');

// Placeholder routes for three modules
app.get('/api/group-therapy', (req, res) => {
  res.json({ message: 'Group Therapy Optimizer endpoint' });
});

app.use('/api/interventions', interventionRoutes);

app.get('/api/aftercare', (req, res) => {
  res.json({ message: 'Therapeutic Aftercare Planner endpoint' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Backend listening on port ${PORT}`);
});
