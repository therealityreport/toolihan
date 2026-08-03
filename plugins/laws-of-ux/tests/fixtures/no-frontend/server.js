// Backend-only fixture: no view layer, no CSS, no components.
// The auditor should detect "no frontend surface" and refuse with no grade.
const express = require('express');
const { Pool } = require('pg');

const app = express();
const pool = new Pool();
app.use(express.json());

app.get('/api/orders', async (req, res) => {
  const { rows } = await pool.query('SELECT id, total FROM orders ORDER BY id DESC LIMIT 50');
  res.json(rows);
});

app.post('/api/orders', async (req, res) => {
  const { total } = req.body;
  const { rows } = await pool.query('INSERT INTO orders(total) VALUES($1) RETURNING id', [total]);
  res.status(201).json({ id: rows[0].id });
});

app.listen(process.env.PORT || 3000);
