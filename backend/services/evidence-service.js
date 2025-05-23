const fs = require('fs');
const path = require('path');

const cacheFile = path.join(__dirname, '..', 'openEvidence-cache.json');
let cache = {};
try {
  cache = JSON.parse(fs.readFileSync(cacheFile, 'utf8'));
} catch (e) {
  cache = {};
}

async function callGemini(prompt) {
  // Placeholder for Gemini API call
  return `Gemini summary for ${prompt}`;
}

async function callOpenEvidence(prompt) {
  // Placeholder for OpenEvidence API call
  return { evidence: `OpenEvidence result for ${prompt}` };
}

async function getEvidence(intervention_type) {
  if (cache[intervention_type]) {
    return cache[intervention_type];
  }

  const gemini = await callGemini(intervention_type);
  const openEvidence = await callOpenEvidence(intervention_type);

  const result = { intervention_type, gemini, openEvidence };
  cache[intervention_type] = result;
  fs.writeFileSync(cacheFile, JSON.stringify(cache, null, 2));
  return result;
}

module.exports = { getEvidence };
