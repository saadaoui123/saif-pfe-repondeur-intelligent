const pool = require('../db');

async function createPatient(name, email, phone) {
  const conn = await pool.getConnection();
  try {
    const [rows] = await conn.query(
      `INSERT INTO patient (name, email, phone) VALUES (?, ?, ?)`,
      [name, email, phone]
    );
    return rows.insertId;
  } finally {
    conn.release();
  }
}

module.exports = { createPatient };