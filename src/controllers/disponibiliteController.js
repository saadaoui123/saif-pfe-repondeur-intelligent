const db = require("../db");

const getCreneauxLibres = async (req, res) => {
  const { doctor_id, date } = req.query;
  if (!doctor_id || !date)
    return res.status(400).json({ error: "doctor_id et date requis" });
  try {
    const [dispos] = await db.query(
      "SELECT * FROM disponibilite WHERE doctor_id = ? AND date = ?",
      [doctor_id, date]
    );
    const [rdvPris] = await db.query(
      "SELECT time FROM appointments WHERE doctor_id = ? AND date = ? AND status = 'planned'",
      [doctor_id, date]
    );
    const heuresPrises = rdvPris.map((r) => r.time);
    const creneaux = [];
    for (const dispo of dispos) {
      let current = timeToMin(dispo.start_time);
      const end = timeToMin(dispo.end_time);
      while (current + 30 <= end) {
        const heure = minToTime(current);
        if (!heuresPrises.includes(heure)) creneaux.push(heure);
        current += 30;
      }
    }
    res.json({ date, doctor_id, creneaux_libres: creneaux, total: creneaux.length });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

function timeToMin(t) {
  const [h, m] = t.toString().split(":").map(Number);
  return h * 60 + m;
}
function minToTime(m) {
  return `${String(Math.floor(m/60)).padStart(2,"0")}:${String(m%60).padStart(2,"0")}:00`;
}

module.exports = { getCreneauxLibres };
