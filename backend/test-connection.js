require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');

const url = process.env.SUPABASE_URL;
const key = process.env.SUPABASE_KEY || process.env.SUPABASE_ANON_KEY;

if (!url || !key) {
  console.error('Missing Supabase credentials. Please set SUPABASE_URL and SUPABASE_KEY.');
  process.exit(1);
}

const supabase = createClient(url, key);

async function testConnection() {
  try {
    const { data, error } = await supabase.from('practices').select('*').limit(1);
    if (error) throw error;
    console.log('Connection to Supabase successful. Sample data:', data);
  } catch (err) {
    console.error('Error connecting to Supabase:', err);
  }
}

testConnection();

