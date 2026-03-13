const pool = require('../db');

async function createAppointment(patientId, doctorId, date, time, reason) {
  const conn = await pool.getConnection();
  try {
    const [rows] = await conn.query(
      `INSERT INTO appointments (patient_id, doctor_id, date, time, reason) 
       VALUES (?, ?, ?, ?, ?)`,
      [patientId, doctorId, date, time, reason]
    );
    return rows.insertId;
  } finally {
    conn.release();
  }
}

module.exports = { createAppointment };