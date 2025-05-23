#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { supabase } = require('./supabaseClient');

async function generateReport() {
  const { data, error } = await supabase.from('integrated_analytics').select('*');
  if (error) {
    console.error(error.message);
    process.exit(1);
  }
  const counts = {};
  data.forEach(row => {
    counts[row.metric_type] = (counts[row.metric_type] || 0) + 1;
  });
  const report = { generated_at: new Date().toISOString(), counts };
  const outPath = path.join(__dirname, 'analytics-report.json');
  fs.writeFileSync(outPath, JSON.stringify(report, null, 2));
  console.log('Analytics exported to', outPath);
}

if (require.main === module) {
  generateReport();
}
