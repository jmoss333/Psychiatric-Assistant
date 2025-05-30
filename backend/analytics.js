require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_KEY || process.env.SUPABASE_ANON_KEY;

if (!SUPABASE_URL || !SUPABASE_KEY) {
  console.error('Please set SUPABASE_URL and SUPABASE_KEY in your .env file.');
  process.exit(1);
}

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

async function run() {
  const { count, error: countError } = await supabase
    .from('interventions')
    .select('*', { count: 'exact', head: true });

  if (countError) {
    console.error('Error counting interventions:', countError.message);
    return;
  }

  console.log('\n=== Intervention Analytics ===');
  console.log('Total interventions:', count);

  if (!count) {
    console.log('No interventions found.');
    return;
  }

  // fetch grouped stats
  const { data, error } = await supabase
    .from('interventions')
    .select('intervention_type, duration_minutes, response_rating');

  if (error) {
    console.error('Error fetching interventions:', error.message);
    return;
  }

  // group by type
  const stats = {};
  data.forEach((row) => {
    const key = row.intervention_type;
    if (!stats[key]) {
      stats[key] = { count: 0, durationTotal: 0, ratingTotal: 0 };
    }
    stats[key].count += 1;
    stats[key].durationTotal += row.duration_minutes;
    stats[key].ratingTotal += row.response_rating;
  });

  Object.entries(stats).forEach(([type, values]) => {
    const avgDuration = values.durationTotal / values.count;
    const avgRating = values.ratingTotal / values.count;
    console.log(`\n--- ${type} ---`);
    console.log('Count:', values.count);
    console.log('Average Duration (min):', avgDuration.toFixed(1));
    console.log('Average Rating:', avgRating.toFixed(2));
  });
}

run();
