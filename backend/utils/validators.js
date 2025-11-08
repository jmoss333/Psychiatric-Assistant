const Joi = require('joi');

// Therapist registration/login validation
const therapistSchema = Joi.object({
  email: Joi.string().email().required(),
  password: Joi.string().min(8).required(),
  first_name: Joi.string().max(100),
  last_name: Joi.string().max(100),
});

// Clinic creation validation
const clinicSchema = Joi.object({
  name: Joi.string().max(255).required(),
  address: Joi.object({
    street: Joi.string(),
    city: Joi.string(),
    state: Joi.string(),
    zip: Joi.string(),
    country: Joi.string(),
  }),
  phone: Joi.string().max(20),
  email: Joi.string().email(),
  license_number: Joi.string().max(100),
});

// Patient intake validation
const patientSchema = Joi.object({
  demographics: Joi.object({
    first_name: Joi.string().required(),
    last_name: Joi.string().required(),
    date_of_birth: Joi.date(),
    gender: Joi.string().valid('male', 'female', 'non-binary', 'prefer_not_to_say'),
    contact_email: Joi.string().email(),
    contact_phone: Joi.string(),
  }).required(),
  clinical_profile: Joi.object({
    dsm5_codes: Joi.array().items(Joi.string()),
    medical_history: Joi.string(),
    current_medications: Joi.array(),
  }).required(),
  current_presentations: Joi.object(),
  treatment_history: Joi.object(),
  preferences: Joi.object(),
});

// Clinical scenario validation
const scenarioSchema = Joi.object({
  scenario_type: Joi.string().valid('free_text', 'structured_form', 'import', 'transcription').required(),
  raw_input: Joi.string().when('scenario_type', { is: 'free_text', then: Joi.required() }),
  presenting_problems: Joi.array().items(Joi.string()),
  dsm5_codes: Joi.array().items(Joi.string()),
  symptom_severity: Joi.object(),
  assessment_scales: Joi.object(),
  provider_notes: Joi.string(),
  urgent_flags: Joi.array().items(Joi.string()),
});

const validate = (schema) => {
  return (req, res, next) => {
    const { error, value } = schema.validate(req.body);
    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }
    req.validatedBody = value;
    next();
  };
};

module.exports = {
  validate,
  therapistSchema,
  clinicSchema,
  patientSchema,
  scenarioSchema,
};
