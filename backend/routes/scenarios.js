const express = require('express');
const { v4: uuidv4 } = require('uuid');
const pool = require('../db/config');
const { authenticateToken } = require('../middleware/auth');
const { validate, scenarioSchema } = require('../utils/validators');

const router = express.Router();

// Create a clinical scenario (flexible input)
router.post('/', authenticateToken, validate(scenarioSchema), async (req, res) => {
  try {
    const { therapist_id } = req.therapist;
    const {
      patient_id,
      scenario_type,
      raw_input,
      presenting_problems,
      dsm5_codes,
      symptom_severity,
      psychosocial_stressors,
      protective_factors,
      assessment_scales,
      prior_responses,
      family_history,
      substance_use,
      trauma_history,
      provider_notes,
      urgent_flags,
      session_number,
    } = req.validatedBody;

    // Verify patient exists and is in same clinic
    const patientResult = await pool.query(
      `SELECT p.clinic_id FROM unified_patient_profiles p
       INNER JOIN therapists t ON p.clinic_id = t.clinic_id
       WHERE p.patient_id = $1 AND t.therapist_id = $2`,
      [patient_id, therapist_id]
    );

    if (patientResult.rows.length === 0) {
      return res.status(404).json({ error: 'Patient not found or unauthorized' });
    }

    const scenarioId = uuidv4();

    const result = await pool.query(
      `INSERT INTO clinical_scenarios
       (scenario_id, patient_id, therapist_id, scenario_type, raw_input,
        presenting_problems, dsm5_codes, symptom_severity, psychosocial_stressors,
        protective_factors, assessment_scales, prior_responses, family_history,
        substance_use, trauma_history, provider_notes, urgent_flags, session_number)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18)
       RETURNING *`,
      [
        scenarioId,
        patient_id,
        therapist_id,
        scenario_type,
        raw_input || null,
        JSON.stringify(presenting_problems || []),
        JSON.stringify(dsm5_codes || []),
        JSON.stringify(symptom_severity || {}),
        JSON.stringify(psychosocial_stressors || {}),
        JSON.stringify(protective_factors || {}),
        JSON.stringify(assessment_scales || {}),
        JSON.stringify(prior_responses || {}),
        JSON.stringify(family_history || {}),
        JSON.stringify(substance_use || {}),
        JSON.stringify(trauma_history || {}),
        provider_notes || null,
        JSON.stringify(urgent_flags || []),
        session_number || null,
      ]
    );

    const scenario = result.rows[0];

    res.status(201).json({
      message: 'Clinical scenario created successfully',
      scenario,
    });
  } catch (error) {
    console.error('Scenario creation error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get scenario by ID
router.get('/:scenario_id', authenticateToken, async (req, res) => {
  try {
    const { scenario_id } = req.params;

    const result = await pool.query(
      'SELECT * FROM clinical_scenarios WHERE scenario_id = $1',
      [scenario_id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Scenario not found' });
    }

    res.json({ scenario: result.rows[0] });
  } catch (error) {
    console.error('Error fetching scenario:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Update scenario
router.put('/:scenario_id', authenticateToken, async (req, res) => {
  try {
    const { scenario_id } = req.params;
    const {
      presenting_problems,
      dsm5_codes,
      symptom_severity,
      assessment_scales,
      provider_notes,
      urgent_flags,
    } = req.body;

    const result = await pool.query(
      `UPDATE clinical_scenarios
       SET presenting_problems = COALESCE($2, presenting_problems),
           dsm5_codes = COALESCE($3, dsm5_codes),
           symptom_severity = COALESCE($4, symptom_severity),
           assessment_scales = COALESCE($5, assessment_scales),
           provider_notes = COALESCE($6, provider_notes),
           urgent_flags = COALESCE($7, urgent_flags),
           updated_at = NOW()
       WHERE scenario_id = $1
       RETURNING *`,
      [
        scenario_id,
        presenting_problems ? JSON.stringify(presenting_problems) : null,
        dsm5_codes ? JSON.stringify(dsm5_codes) : null,
        symptom_severity ? JSON.stringify(symptom_severity) : null,
        assessment_scales ? JSON.stringify(assessment_scales) : null,
        provider_notes,
        urgent_flags ? JSON.stringify(urgent_flags) : null,
      ]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Scenario not found' });
    }

    res.json({
      message: 'Scenario updated successfully',
      scenario: result.rows[0],
    });
  } catch (error) {
    console.error('Error updating scenario:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get all scenarios for a patient
router.get('/patient/:patient_id', authenticateToken, async (req, res) => {
  try {
    const { patient_id } = req.params;

    const result = await pool.query(
      `SELECT * FROM clinical_scenarios
       WHERE patient_id = $1
       ORDER BY created_at DESC`,
      [patient_id]
    );

    res.json({
      count: result.rows.length,
      scenarios: result.rows,
    });
  } catch (error) {
    console.error('Error fetching scenarios:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;
