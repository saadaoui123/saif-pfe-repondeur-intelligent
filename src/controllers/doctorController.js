const pool = require('../db');

async function getDoctors() {
  const conn = await pool.getConnection();
  try {
    const [rows] = await conn.query(`SELECT * FROM doctor`);
    return rows;
  } finally {
    conn.release();
  }
}

module.exports = { getDoctors };