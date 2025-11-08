const express = require('express');
const bcryptjs = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');
const pool = require('../db/config');
const { validate, therapistSchema } = require('../utils/validators');

const router = express.Router();

// Register a new therapist
router.post('/register', validate(therapistSchema), async (req, res) => {
  try {
    const { email, password, first_name, last_name } = req.validatedBody;

    // Check if therapist already exists
    const existingTherapist = await pool.query(
      'SELECT * FROM therapists WHERE email = $1',
      [email]
    );

    if (existingTherapist.rows.length > 0) {
      return res.status(409).json({ error: 'Therapist with this email already exists' });
    }

    // Hash password
    const hashedPassword = await bcryptjs.hash(password, 10);

    // Create therapist
    const therapistId = uuidv4();
    const result = await pool.query(
      `INSERT INTO therapists (therapist_id, email, password_hash, first_name, last_name)
       VALUES ($1, $2, $3, $4, $5)
       RETURNING therapist_id, email, first_name, last_name`,
      [therapistId, email, hashedPassword, first_name || '', last_name || '']
    );

    const therapist = result.rows[0];

    // Generate JWT token
    const token = jwt.sign(
      { therapist_id: therapist.therapist_id, email: therapist.email },
      process.env.JWT_SECRET || 'your-secret-key',
      { expiresIn: '24h' }
    );

    res.status(201).json({
      message: 'Therapist registered successfully',
      token,
      therapist,
    });
  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Login therapist
router.post('/login', validate(therapistSchema), async (req, res) => {
  try {
    const { email, password } = req.validatedBody;

    // Find therapist by email
    const result = await pool.query(
      'SELECT * FROM therapists WHERE email = $1',
      [email]
    );

    if (result.rows.length === 0) {
      return res.status(401).json({ error: 'Invalid email or password' });
    }

    const therapist = result.rows[0];

    // Verify password
    const passwordMatch = await bcryptjs.compare(password, therapist.password_hash);
    if (!passwordMatch) {
      return res.status(401).json({ error: 'Invalid email or password' });
    }

    // Update last login
    await pool.query(
      'UPDATE therapists SET last_login = NOW() WHERE therapist_id = $1',
      [therapist.therapist_id]
    );

    // Generate JWT token
    const token = jwt.sign(
      { therapist_id: therapist.therapist_id, email: therapist.email },
      process.env.JWT_SECRET || 'your-secret-key',
      { expiresIn: '24h' }
    );

    res.json({
      message: 'Login successful',
      token,
      therapist: {
        therapist_id: therapist.therapist_id,
        email: therapist.email,
        first_name: therapist.first_name,
        last_name: therapist.last_name,
      },
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Logout (optional - just client-side token deletion in production)
router.post('/logout', (req, res) => {
  res.json({ message: 'Logout successful' });
});

module.exports = router;
