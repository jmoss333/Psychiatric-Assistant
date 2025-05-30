require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');
const { randomUUID } = require('crypto');

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_KEY || process.env.SUPABASE_ANON_KEY;

if (!SUPABASE_URL || !SUPABASE_KEY) {
  console.error('Please set SUPABASE_URL and SUPABASE_KEY in your .env file.');
  process.exit(1);
}

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

const interventionTypes = [
  'Crisis De-escalation',
  'Medication Education',
  'Cognitive Restructuring',
  'Safety Planning',
  'Motivational Interviewing',
  'Behavioral Activation'
];

const settings = ['Bedside', 'Group Room', 'Hallway', 'Phone', 'Nursing Station'];

function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

const now = new Date();
const interventions = Array.from({ length: 20 }, (_, i) => {
  const date = new Date(now);
  date.setDate(now.getDate() - randomInt(0, 6));
  date.setHours(randomInt(0, 23), randomInt(0, 59), randomInt(0, 59), 0);

  return {
    patient_id: randomUUID(),
    provider_id: randomUUID(),
    intervention_type: interventionTypes[randomInt(0, interventionTypes.length - 1)],
    duration_minutes: randomInt(15, 60),
    setting: settings[randomInt(0, settings.length - 1)],
    response_rating: randomInt(3, 5),
    notes: `Sample note ${i + 1}`,
    created_at: date.toISOString()
  };
});

async function seed() {
  const { data, error } = await supabase.from('interventions').insert(interventions);
  if (error) {
    console.error('Error inserting interventions:', error.message);
  } else {
    console.log(`Inserted ${data.length} interventions.`);
  }
}

seed();
