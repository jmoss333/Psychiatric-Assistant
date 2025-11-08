#!/usr/bin/env node

/**
 * Phase 1 Automated Test Runner
 *
 * Tests all core endpoints and validates responses
 * Run with: node test-runner.js
 */

const http = require('http');
const querystring = require('querystring');

const BASE_URL = 'http://localhost:3000';
const API_BASE = `${BASE_URL}/api/v1`;

// Color codes for terminal output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

// Test results tracking
let testsPassed = 0;
let testsFailed = 0;
const failures = [];

// Store tokens and IDs for use across tests
let authToken = null;
let therapistId = null;
let clinicId = null;
let patientId = null;
let scenarioId = null;

/**
 * Make HTTP request to API
 */
function makeRequest(method, path, body = null, headers = {}) {
  return new Promise((resolve, reject) => {
    const url = new URL(path.startsWith('http') ? path : `${API_BASE}${path}`);

    const options = {
      hostname: url.hostname,
      port: url.port || 3000,
      path: url.pathname + url.search,
      method: method,
      headers: {
        'Content-Type': 'application/json',
        ...headers,
      },
    };

    if (authToken && !headers['Authorization']) {
      options.headers['Authorization'] = `Bearer ${authToken}`;
    }

    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => {
        data += chunk;
      });
      res.on('end', () => {
        try {
          const response = {
            status: res.statusCode,
            headers: res.headers,
            body: data ? JSON.parse(data) : null,
          };
          resolve(response);
        } catch (e) {
          resolve({
            status: res.statusCode,
            headers: res.headers,
            body: data,
            error: e.message,
          });
        }
      });
    });

    req.on('error', reject);

    if (body) {
      req.write(JSON.stringify(body));
    }
    req.end();
  });
}

/**
 * Assert a condition and log result
 */
function assert(condition, message) {
  if (condition) {
    console.log(`  ${colors.green}✓${colors.reset} ${message}`);
    testsPassed++;
  } else {
    console.log(`  ${colors.red}✗${colors.reset} ${message}`);
    testsFailed++;
    failures.push(message);
  }
}

/**
 * Test suite runner
 */
async function runTests() {
  console.log(`\n${colors.cyan}╔════════════════════════════════════════╗${colors.reset}`);
  console.log(`${colors.cyan}║  Smart Communicator Phase 1 Test Suite  ║${colors.reset}`);
  console.log(`${colors.cyan}╚════════════════════════════════════════╝${colors.reset}\n`);

  try {
    // Test 1: Health Check
    await testHealthCheck();

    // Test 2: Authentication
    await testAuthentication();

    // Test 3: Clinic Management
    await testClinicManagement();

    // Test 4: Patient Management
    await testPatientManagement();

    // Test 5: Clinical Scenarios
    await testClinicalScenarios();

    // Test 6: Error Handling
    await testErrorHandling();

    // Print summary
    printSummary();
  } catch (error) {
    console.error(`${colors.red}Fatal error:${colors.reset}`, error);
    process.exit(1);
  }
}

/**
 * Test 1: Health Check
 */
async function testHealthCheck() {
  console.log(`${colors.blue}Test 1: Health Check${colors.reset}`);

  const response = await makeRequest('GET', `${BASE_URL}/health`);
  assert(response.status === 200, 'Health check returns 200');
  assert(response.body?.status === 'OK', 'Health check status is OK');
}

/**
 * Test 2: Authentication
 */
async function testAuthentication() {
  console.log(`\n${colors.blue}Test 2: Authentication${colors.reset}`);

  // Register therapist
  const registerResponse = await makeRequest('POST', '/auth/register', {
    email: `therapist-${Date.now()}@test.com`,
    password: 'TestPassword123!',
    first_name: 'Test',
    last_name: 'Therapist',
  });

  assert(registerResponse.status === 201, 'Registration returns 201');
  assert(registerResponse.body?.token, 'Registration returns JWT token');
  assert(registerResponse.body?.therapist?.therapist_id, 'Registration returns therapist ID');

  if (registerResponse.body?.token) {
    authToken = registerResponse.body.token;
    therapistId = registerResponse.body.therapist.therapist_id;
  }

  // Login
  const loginResponse = await makeRequest('POST', '/auth/login', {
    email: registerResponse.body?.therapist?.email,
    password: 'TestPassword123!',
  });

  assert(loginResponse.status === 200, 'Login returns 200');
  assert(loginResponse.body?.token, 'Login returns JWT token');

  // Invalid password
  const invalidLoginResponse = await makeRequest('POST', '/auth/login', {
    email: registerResponse.body?.therapist?.email,
    password: 'WrongPassword',
  });

  assert(invalidLoginResponse.status === 401, 'Invalid password returns 401');

  // Logout
  const logoutResponse = await makeRequest('POST', '/auth/logout', null);
  assert(logoutResponse.status === 200, 'Logout returns 200');
}

/**
 * Test 3: Clinic Management
 */
async function testClinicManagement() {
  console.log(`\n${colors.blue}Test 3: Clinic Management${colors.reset}`);

  // Create clinic
  const createResponse = await makeRequest('POST', '/clinics', {
    name: 'Test Mental Health Clinic',
    address: {
      street: '123 Test St',
      city: 'Test City',
      state: 'TS',
      zip: '12345',
      country: 'USA',
    },
    phone: '+1-555-0100',
    email: 'contact@testclinic.com',
    license_number: 'TEST-2024-001',
  });

  assert(createResponse.status === 201, 'Create clinic returns 201');
  assert(createResponse.body?.clinic?.clinic_id, 'Create clinic returns clinic ID');

  if (createResponse.body?.clinic?.clinic_id) {
    clinicId = createResponse.body.clinic.clinic_id;
  }

  // Get clinics
  const getResponse = await makeRequest('GET', '/clinics');
  assert(getResponse.status === 200, 'Get clinics returns 200');
  assert(Array.isArray(getResponse.body?.clinics), 'Get clinics returns array');

  // Get clinic by ID
  if (clinicId) {
    const getByIdResponse = await makeRequest('GET', `/clinics/${clinicId}`);
    assert(getByIdResponse.status === 200, 'Get clinic by ID returns 200');
    assert(getByIdResponse.body?.clinic?.clinic_id === clinicId, 'Returns correct clinic');
  }

  // Update clinic
  if (clinicId) {
    const updateResponse = await makeRequest('PUT', `/clinics/${clinicId}`, {
      phone: '+1-555-0200',
    });
    assert(updateResponse.status === 200, 'Update clinic returns 200');
  }
}

/**
 * Test 4: Patient Management
 */
async function testPatientManagement() {
  console.log(`\n${colors.blue}Test 4: Patient Management${colors.reset}`);

  // Create patient
  const createResponse = await makeRequest('POST', '/patients', {
    demographics: {
      first_name: 'Test',
      last_name: 'Patient',
      date_of_birth: '1990-05-15',
      gender: 'female',
      contact_email: 'patient@test.com',
      contact_phone: '+1-555-0300',
    },
    clinical_profile: {
      dsm5_codes: ['F41.1'],
      medical_history: 'Test medical history',
      current_medications: ['Medication A'],
    },
    current_presentations: {
      chief_complaint: 'Test complaint',
    },
    treatment_history: {
      prior_therapy: 'None',
    },
    preferences: {
      therapy_modality_preferences: ['CBT'],
    },
  });

  assert(createResponse.status === 201, 'Create patient returns 201');
  assert(createResponse.body?.patient?.patient_id, 'Create patient returns patient ID');

  if (createResponse.body?.patient?.patient_id) {
    patientId = createResponse.body.patient.patient_id;
  }

  // Get patients
  const getResponse = await makeRequest('GET', '/patients');
  assert(getResponse.status === 200, 'Get patients returns 200');
  assert(Array.isArray(getResponse.body?.patients), 'Get patients returns array');

  // Get patient by ID
  if (patientId) {
    const getByIdResponse = await makeRequest('GET', `/patients/${patientId}`);
    assert(getByIdResponse.status === 200, 'Get patient by ID returns 200');
    assert(getByIdResponse.body?.patient?.patient_id === patientId, 'Returns correct patient');
  }

  // Update patient
  if (patientId) {
    const updateResponse = await makeRequest('PUT', `/patients/${patientId}`, {
      current_presentations: {
        chief_complaint: 'Updated complaint',
      },
    });
    assert(updateResponse.status === 200, 'Update patient returns 200');
  }
}

/**
 * Test 5: Clinical Scenarios
 */
async function testClinicalScenarios() {
  console.log(`\n${colors.blue}Test 5: Clinical Scenarios${colors.reset}`);

  if (!patientId) {
    console.log(`  ${colors.yellow}⊘${colors.reset} Skipping - no patient ID`);
    return;
  }

  // Create scenario - Free text
  const createResponse = await makeRequest('POST', '/scenarios', {
    patient_id: patientId,
    scenario_type: 'free_text',
    raw_input: 'Patient reports increased anxiety and sleep disruption.',
    presenting_problems: ['Anxiety', 'Sleep disruption'],
    dsm5_codes: ['F41.1'],
    symptom_severity: {
      anxiety: '7/10',
      sleep_disruption: '6/10',
    },
    assessment_scales: {
      phq9: 14,
      gad7: 16,
    },
    provider_notes: 'Patient motivated for treatment',
    session_number: 1,
  });

  assert(createResponse.status === 201, 'Create scenario returns 201');
  assert(createResponse.body?.scenario?.scenario_id, 'Create scenario returns scenario ID');

  if (createResponse.body?.scenario?.scenario_id) {
    scenarioId = createResponse.body.scenario.scenario_id;
  }

  // Get scenario
  if (scenarioId) {
    const getResponse = await makeRequest('GET', `/scenarios/${scenarioId}`);
    assert(getResponse.status === 200, 'Get scenario returns 200');
    assert(getResponse.body?.scenario?.scenario_id === scenarioId, 'Returns correct scenario');
  }

  // Update scenario
  if (scenarioId) {
    const updateResponse = await makeRequest('PUT', `/scenarios/${scenarioId}`, {
      assessment_scales: {
        phq9: 12,
        gad7: 14,
      },
    });
    assert(updateResponse.status === 200, 'Update scenario returns 200');
  }

  // Get patient scenarios
  if (patientId) {
    const getPatientScenariosResponse = await makeRequest('GET', `/scenarios/patient/${patientId}`);
    assert(getPatientScenariosResponse.status === 200, 'Get patient scenarios returns 200');
    assert(Array.isArray(getPatientScenariosResponse.body?.scenarios), 'Returns array of scenarios');
  }
}

/**
 * Test 6: Error Handling
 */
async function testErrorHandling() {
  console.log(`\n${colors.blue}Test 6: Error Handling${colors.reset}`);

  // Missing token
  const noTokenResponse = await makeRequest('GET', '/patients', null, { 'Authorization': '' });
  assert(noTokenResponse.status === 401, 'Missing token returns 401');

  // Invalid token
  const invalidTokenResponse = await makeRequest('GET', '/patients', null, {
    'Authorization': 'Bearer invalid-token',
  });
  assert(invalidTokenResponse.status === 403, 'Invalid token returns 403');

  // Invalid scenario type
  if (patientId) {
    const invalidTypeResponse = await makeRequest('POST', '/scenarios', {
      patient_id: patientId,
      scenario_type: 'invalid_type',
      raw_input: 'test',
    });
    assert(invalidTypeResponse.status === 400, 'Invalid scenario type returns 400');
  }

  // Not found
  const notFoundResponse = await makeRequest('GET', '/patients/nonexistent-uuid');
  assert(notFoundResponse.status === 404, 'Nonexistent patient returns 404');

  // Duplicate email registration
  const email = `duplicate-${Date.now()}@test.com`;
  await makeRequest('POST', '/auth/register', {
    email: email,
    password: 'Password123!',
    first_name: 'First',
    last_name: 'Last',
  });

  const duplicateResponse = await makeRequest('POST', '/auth/register', {
    email: email,
    password: 'Password456!',
    first_name: 'Another',
    last_name: 'Person',
  });
  assert(duplicateResponse.status === 409, 'Duplicate email returns 409');
}

/**
 * Print test summary
 */
function printSummary() {
  console.log(`\n${colors.cyan}════════════════════════════════════════${colors.reset}`);
  console.log(`${colors.cyan}Test Summary${colors.reset}`);
  console.log(`${colors.cyan}════════════════════════════════════════${colors.reset}`);

  console.log(`${colors.green}✓ Passed:${colors.reset} ${testsPassed}`);
  console.log(`${colors.red}✗ Failed:${colors.reset} ${testsFailed}`);
  console.log(`Total: ${testsPassed + testsFailed}\n`);

  if (testsFailed > 0) {
    console.log(`${colors.red}Failed Tests:${colors.reset}`);
    failures.forEach((failure) => {
      console.log(`  - ${failure}`);
    });
  }

  const percentage = testsPassed / (testsPassed + testsFailed) * 100;
  const passColor = percentage >= 90 ? colors.green : percentage >= 70 ? colors.yellow : colors.red;
  console.log(`\nPass Rate: ${passColor}${percentage.toFixed(1)}%${colors.reset}\n`);

  process.exit(testsFailed > 0 ? 1 : 0);
}

// Run tests
runTests().catch((error) => {
  console.error(`${colors.red}Test error:${colors.reset}`, error.message);
  process.exit(1);
});
