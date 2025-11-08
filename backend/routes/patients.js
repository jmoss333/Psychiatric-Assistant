const express = require('express');
const { v4: uuidv4 } = require('uuid');
const pool = require('../db/config');
const { authenticateToken } = require('../middleware/auth');
const { validate, patientSchema } = require('../utils/validators');

const router = express.Router();

// Create a new patient (intake)
router.post('/', authenticateToken, validate(patientSchema), async (req, res) => {
  try {
    const { demographics, clinical_profile, current_presentations, treatment_history, preferences } = req.validatedBody;
    const { therapist_id } = req.therapist;

    // Get therapist's clinic
    const therapistResult = await pool.query(
      'SELECT clinic_id FROM therapists WHERE therapist_id = $1',
      [therapist_id]
    );

    if (therapistResult.rows.length === 0) {
      return res.status(404).json({ error: 'Therapist not found' });
    }

    const clinicId = therapistResult.rows[0].clinic_id;
    const patientId = uuidv4();

    const result = await pool.query(
      `INSERT INTO unified_patient_profiles
       (patient_id, clinic_id, demographics, clinical_profile, current_presentations, treatment_history, preferences)
       VALUES ($1, $2, $3, $4, $5, $6, $7)
       RETURNING *`,
      [
        patientId,
        clinicId,
        JSON.stringify(demographics),
        JSON.stringify(clinical_profile),
        JSON.stringify(current_presentations || {}),
        JSON.stringify(treatment_history || {}),
        JSON.stringify(preferences || {}),
      ]
    );

    res.status(201).json({
      message: 'Patient created successfully',
      patient: result.rows[0],
    });
  } catch (error) {
    console.error('Patient creation error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get all patients for a therapist
router.get('/', authenticateToken, async (req, res) => {
  try {
    const { therapist_id } = req.therapist;

    const result = await pool.query(
      `SELECT p.* FROM unified_patient_profiles p
       INNER JOIN therapists t ON p.clinic_id = t.clinic_id
       WHERE t.therapist_id = $1
       ORDER BY p.created_at DESC`,
      [therapist_id]
    );

    res.json({
      count: result.rows.length,
      patients: result.rows,
    });
  } catch (error) {
    console.error('Error fetching patients:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get patient by ID
router.get('/:patient_id', authenticateToken, async (req, res) => {
  try {
    const { patient_id } = req.params;

    const result = await pool.query(
      'SELECT * FROM unified_patient_profiles WHERE patient_id = $1',
      [patient_id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Patient not found' });
    }

    res.json({ patient: result.rows[0] });
  } catch (error) {
    console.error('Error fetching patient:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Update patient
router.put('/:patient_id', authenticateToken, async (req, res) => {
  try {
    const { patient_id } = req.params;
    const {
      demographics,
      clinical_profile,
      current_presentations,
      treatment_history,
      preferences,
      status,
    } = req.body;

    const result = await pool.query(
      `UPDATE unified_patient_profiles
       SET demographics = COALESCE($2, demographics),
           clinical_profile = COALESCE($3, clinical_profile),
           current_presentations = COALESCE($4, current_presentations),
           treatment_history = COALESCE($5, treatment_history),
           preferences = COALESCE($6, preferences),
           status = COALESCE($7, status),
           updated_at = NOW()
       WHERE patient_id = $1
       RETURNING *`,
      [
        patient_id,
        demographics ? JSON.stringify(demographics) : null,
        clinical_profile ? JSON.stringify(clinical_profile) : null,
        current_presentations ? JSON.stringify(current_presentations) : null,
        treatment_history ? JSON.stringify(treatment_history) : null,
        preferences ? JSON.stringify(preferences) : null,
        status,
      ]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Patient not found' });
    }

    res.json({
      message: 'Patient updated successfully',
      patient: result.rows[0],
    });
  } catch (error) {
    console.error('Error updating patient:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get patient's clinical scenarios
router.get('/:patient_id/scenarios', authenticateToken, async (req, res) => {
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
