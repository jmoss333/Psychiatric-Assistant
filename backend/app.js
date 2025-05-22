const express = require('express');
const app = express();
app.use(express.json());

// Placeholder routes for three modules
app.get('/api/group-therapy', (req, res) => {
  res.json({ message: 'Group Therapy Optimizer endpoint' });
});

app.get('/api/intervention', (req, res) => {
  res.json({ message: 'Therapeutic Intervention Tracker endpoint' });
});

app.get('/api/aftercare', (req, res) => {
  res.json({ message: 'Therapeutic Aftercare Planner endpoint' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Backend listening on port ${PORT}`);
});
