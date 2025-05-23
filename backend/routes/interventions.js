const express = require('express');
const router = express.Router();
const { supabase } = require('../supabaseClient');

router.post('/quick-log', async (req, res) => {
  const { patient_id, provider_id, intervention_type, notes } = req.body;
  if (!patient_id || !provider_id || !intervention_type) {
    return res.status(400).json({ error: 'Missing required fields' });
  }

  const { data, error } = await supabase
    .from('interventions')
    .insert([{ patient_id, provider_id, intervention_type, notes }])
    .single();

  if (error) {
    return res.status(500).json({ error: error.message });
  }
  res.json(data);
});

router.get('/recent', async (_req, res) => {
  const { data, error } = await supabase
    .from('interventions')
    .select('*')
    .order('created_at', { ascending: false })
    .limit(10);

  if (error) {
    return res.status(500).json({ error: error.message });
  }
  res.json(data);
});

module.exports = router;
