const express = require('express');
const router = express.Router();
const { upsertDisponibilite, getDisponibilite } = require('../controllers/disponibiliteController');
const { getDoctors } = require('../controllers/doctorController');
const { createPatient } = require('../controllers/patientController');
const { createAppointment } = require('../controllers/appointmentController');

// Doctor routes
router.get('/doctors', async (req, res) => {
  try {
    const doctors = await getDoctors();
    res.json(doctors);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Disponibilite routes
router.post('/syncDisponibilite', async (req, res) => {
  try {
    const { doctorId, date, startTime, endTime, source, googleEventId } = req.body;
    await upsertDisponibilite(doctorId, date, startTime, endTime, source, googleEventId);
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.get('/disponibilite/:doctorId/:date', async (req, res) => {
  try {
    const disponibilites = await getDisponibilite(req.params.doctorId, req.params.date);
    res.json(disponibilites);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Patient route
router.post('/patients', async (req, res) => {
  try {
    const { name, email, phone } = req.body;
    const id = await createPatient(name, email, phone);
    res.json({ patientId: id });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Appointment route
router.post('/appointments', async (req, res) => {
  try {
    const { patientId, doctorId, date, time, reason } = req.body;
    const id = await createAppointment(patientId, doctorId, date, time, reason);
    res.json({ appointmentId: id });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;