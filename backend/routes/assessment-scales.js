const express = require('express');
const pool = require('../db/config');
const { authenticateToken } = require('../middleware/auth');

const router = express.Router();

// Get all assessment scales (optionally filtered by category)
router.get('/', authenticateToken, async (req, res) => {
  try {
    const { category } = req.query;

    let query = 'SELECT * FROM assessment_scales';
    const params = [];

    if (category) {
      query += ' WHERE category = $1';
      params.push(category);
    }

    query += ' ORDER BY category, name';

    const result = await pool.query(query, params);

    res.json({
      count: result.rows.length,
      scales: result.rows,
    });
  } catch (error) {
    console.error('Error fetching assessment scales:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get assessment scale by ID
router.get('/:scale_id', authenticateToken, async (req, res) => {
  try {
    const { scale_id } = req.params;

    const result = await pool.query(
      'SELECT * FROM assessment_scales WHERE scale_id = $1',
      [scale_id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Assessment scale not found' });
    }

    res.json({ scale: result.rows[0] });
  } catch (error) {
    console.error('Error fetching assessment scale:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get assessment scale by abbreviation (e.g., PHQ-9)
router.get('/abbreviation/:abbr', authenticateToken, async (req, res) => {
  try {
    const { abbr } = req.params;

    const result = await pool.query(
      'SELECT * FROM assessment_scales WHERE abbreviation = $1',
      [abbr.toUpperCase()]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Assessment scale not found' });
    }

    res.json({ scale: result.rows[0] });
  } catch (error) {
    console.error('Error fetching assessment scale:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get assessment scales by category
router.get('/category/:category', authenticateToken, async (req, res) => {
  try {
    const { category } = req.params;

    const result = await pool.query(
      'SELECT * FROM assessment_scales WHERE category = $1 ORDER BY name',
      [category.toLowerCase()]
    );

    res.json({
      category,
      count: result.rows.length,
      scales: result.rows,
    });
  } catch (error) {
    console.error('Error fetching assessment scales:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get all unique categories
router.get('/reference/categories', authenticateToken, async (req, res) => {
  try {
    const result = await pool.query(
      `SELECT DISTINCT category FROM assessment_scales
       ORDER BY category`
    );

    const categories = result.rows.map((row) => row.category);

    res.json({
      categories,
      count: categories.length,
    });
  } catch (error) {
    console.error('Error fetching categories:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;
