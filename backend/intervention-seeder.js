const path = require('path');
const fs = require('fs');
const { supabase } = require('./supabaseClient');

function validatePatient(p) {
  return p && p.id && p.name && p.email;
}

function validateProvider(p) {
  return p && p.id && p.name && p.email;
}

async function seedInterventions() {
  const seedPath = path.join(__dirname, '../db/interventions-seed.json');
  const raw = fs.readFileSync(seedPath, 'utf8');
  const { patients = [], providers = [] } = JSON.parse(raw);

  const validPatients = patients.filter(validatePatient);
  const validProviders = providers.filter(validateProvider);

  if (validPatients.length) {
    await supabase.from('patients').upsert(validPatients, { onConflict: 'id' });
  }
  if (validProviders.length) {
    await supabase.from('providers').upsert(validProviders, { onConflict: 'id' });
  }
}

if (require.main === module) {
  seedInterventions()
    .then(() => {
      console.log('Intervention seed completed');
    })
    .catch((err) => {
      console.error(err);
      process.exit(1);
    });
}

module.exports = { seedInterventions, validatePatient, validateProvider };
