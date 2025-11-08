const express = require('express');
const { v4: uuidv4 } = require('uuid');
const pool = require('../db/config');
const { authenticateToken } = require('../middleware/auth');
const { validate, clinicSchema } = require('../utils/validators');

const router = express.Router();

// Create a new clinic
router.post('/', authenticateToken, validate(clinicSchema), async (req, res) => {
  try {
    const { name, address, phone, email, license_number } = req.validatedBody;

    const clinicId = uuidv4();
    const result = await pool.query(
      `INSERT INTO clinics (clinic_id, name, address, phone, email, license_number)
       VALUES ($1, $2, $3, $4, $5, $6)
       RETURNING *`,
      [clinicId, name, JSON.stringify(address || {}), phone, email, license_number]
    );

    res.status(201).json({
      message: 'Clinic created successfully',
      clinic: result.rows[0],
    });
  } catch (error) {
    console.error('Clinic creation error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get all clinics for a therapist
router.get('/', authenticateToken, async (req, res) => {
  try {
    const { therapist_id } = req.therapist;

    const result = await pool.query(
      `SELECT DISTINCT c.* FROM clinics c
       INNER JOIN therapists t ON c.clinic_id = t.clinic_id
       WHERE t.therapist_id = $1`,
      [therapist_id]
    );

    res.json({ clinics: result.rows });
  } catch (error) {
    console.error('Error fetching clinics:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get clinic by ID
router.get('/:clinic_id', authenticateToken, async (req, res) => {
  try {
    const { clinic_id } = req.params;

    const result = await pool.query(
      'SELECT * FROM clinics WHERE clinic_id = $1',
      [clinic_id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Clinic not found' });
    }

    res.json({ clinic: result.rows[0] });
  } catch (error) {
    console.error('Error fetching clinic:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Update clinic
router.put('/:clinic_id', authenticateToken, async (req, res) => {
  try {
    const { clinic_id } = req.params;
    const { name, address, phone, email, license_number, status } = req.body;

    const result = await pool.query(
      `UPDATE clinics
       SET name = COALESCE($2, name),
           address = COALESCE($3, address),
           phone = COALESCE($4, phone),
           email = COALESCE($5, email),
           license_number = COALESCE($6, license_number),
           status = COALESCE($7, status),
           updated_at = NOW()
       WHERE clinic_id = $1
       RETURNING *`,
      [clinic_id, name, address ? JSON.stringify(address) : null, phone, email, license_number, status]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Clinic not found' });
    }

    res.json({
      message: 'Clinic updated successfully',
      clinic: result.rows[0],
    });
  } catch (error) {
    console.error('Error updating clinic:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;
