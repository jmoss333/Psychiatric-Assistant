require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY
);

const patientId = '123e4567-e89b-12d3-a456-426614174000';
const providerId = '123e4567-e89b-12d3-a456-426614174001';

async function ensureEntities() {
  console.log('🔍 Upserting patient...');
  const { error: patientErr } = await supabase.from('patients').upsert(
    { id: patientId, full_name: 'Test Patient' },
    { onConflict: 'id' }
  );
  if (patientErr) {
    throw new Error('❌ Patient insert failed: ' + patientErr.message);
  }

  console.log('🔍 Upserting provider...');
  const { error: providerErr } = await supabase.from('providers').upsert(
    { id: providerId, full_name: 'Test Provider' },
    { onConflict: 'id' }
  );
  if (providerErr) {
    throw new Error('❌ Provider insert failed: ' + providerErr.message);
  }

  console.log('✅ Patient and provider ready');
}

async function seedInterventions() {
  const interventionTypes = [
    'Crisis De-escalation',
    'Medication Education',
    'Cognitive Restructuring',
    'Safety Planning',
    'Motivational Interviewing',
    'Behavioral Activation'
  ];

  const settings = ['Bedside', 'Group Room', 'Hallway', 'Phone', 'Nursing Station'];
  const interventions = [];

  for (let i = 0; i < 20; i++) {
    const date = new Date();
    date.setDate(date.getDate() - Math.floor(Math.random() * 7));
    interventions.push({
      patient_id: patientId,
      provider_id: providerId,
      intervention_type: interventionTypes[Math.floor(Math.random() * interventionTypes.length)],
      intervention_category: 'therapeutic_communication',
      duration_minutes: 15 + Math.floor(Math.random() * 45),
      setting: settings[Math.floor(Math.random() * settings.length)],
      response_rating: 3 + Math.floor(Math.random() * 3),
      notes: `Sample intervention ${i + 1}`,
      created_at: date.toISOString()
    });
  }

  console.log('📤 Inserting interventions...');
  const { error: insertErr } = await supabase.from('interventions').insert(interventions);
  if (insertErr) {
    throw new Error('❌ Intervention insert failed: ' + insertErr.message);
  }
  console.log('✅ Seeded 20 interventions.');
}

async function seedAll() {
  try {
    await ensureEntities();
    await seedInterventions();
  } catch (err) {
    console.error(err.message);
  }
}

seedAll();
