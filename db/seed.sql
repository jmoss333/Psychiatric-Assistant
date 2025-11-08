-- ============================================================================
-- SEED DATA FOR SMART COMMUNICATOR
-- ============================================================================

-- Insert therapy modalities reference data
INSERT INTO therapy_modalities (
  modality_id, name, abbreviation, description, category, typical_duration_weeks,
  key_phases, core_techniques, evidence_base, contraindications
) VALUES
  (
    gen_random_uuid(),
    'Cognitive Behavioral Therapy',
    'CBT',
    'CBT focuses on identifying and changing negative thought patterns and behaviors that maintain psychological distress.',
    'cognitive-behavioral',
    12,
    '["Assessment and Goal Setting", "Psychoeducation", "Behavioral Activation", "Cognitive Restructuring", "Relapse Prevention"]'::jsonb,
    '["Behavioral Activation", "Cognitive Restructuring", "Thought Records", "Exposure Therapy", "Problem Solving"]'::jsonb,
    '{"efficacy": "Strong", "evidence_level": "A", "conditions": ["Depression", "Anxiety", "PTSD", "OCD", "Eating Disorders"]}'::jsonb,
    '["Active psychosis", "Severe cognitive impairment"]'::jsonb
  ),
  (
    gen_random_uuid(),
    'Dialectical Behavior Therapy',
    'DBT',
    'DBT combines CBT principles with dialectical philosophy and is particularly effective for emotion dysregulation.',
    'cognitive-behavioral',
    12,
    '["Commitment to Treatment", "Mindfulness", "Emotion Regulation", "Distress Tolerance", "Interpersonal Effectiveness"]'::jsonb,
    '["Mindfulness", "Distress Tolerance Skills", "Emotion Regulation Skills", "Interpersonal Effectiveness Skills"]'::jsonb,
    '{"efficacy": "Strong", "evidence_level": "A", "conditions": ["Borderline Personality Disorder", "Suicidality", "Self-Harm"]}'::jsonb,
    '["Unwillingness to commit to treatment structure"]'::jsonb
  ),
  (
    gen_random_uuid(),
    'Acceptance and Commitment Therapy',
    'ACT',
    'ACT focuses on accepting difficult feelings while committing to actions aligned with personal values.',
    'cognitive-behavioral',
    12,
    '["Values Clarification", "Acceptance and Defusion", "Present Moment Awareness", "Committed Action"]'::jsonb,
    '["Mindfulness", "Values Clarification", "Acceptance", "Cognitive Defusion", "Behavioral Activation"]'::jsonb,
    '{"efficacy": "Strong", "evidence_level": "A", "conditions": ["Anxiety", "Depression", "Chronic Pain", "OCD"]}'::jsonb,
    '[]'::jsonb
  ),
  (
    gen_random_uuid(),
    'Psychodynamic Psychotherapy',
    'PDT',
    'Explores unconscious patterns, past relationships, and how they influence current functioning.',
    'psychodynamic',
    16,
    '["Building Therapeutic Alliance", "Exploration of Past", "Pattern Recognition", "Integration and Insight"]'::jsonb,
    '["Free Association", "Dream Analysis", "Transference Exploration", "Interpretation"]'::jsonb,
    '{"efficacy": "Moderate", "evidence_level": "B", "conditions": ["Depression", "Anxiety", "Personality Disorders"]}'::jsonb,
    '["Limited verbal ability", "Acute crisis", "Severe cognitive impairment"]'::jsonb
  ),
  (
    gen_random_uuid(),
    'Emotion-Focused Therapy',
    'EFT',
    'Focuses on identifying, accessing, and transforming core emotional experiences.',
    'psychodynamic',
    12,
    '["Emotion Exploration", "Emotion Regulation", "Resolution of Conflict", "Integration"]'::jsonb,
    '["Experiential Awareness", "Symbolic Expression", "Two-Chair Dialogue", "Emotion Naming"]'::jsonb,
    '{"efficacy": "Strong", "evidence_level": "A", "conditions": ["Anxiety", "Depression", "Trauma", "Relationship Issues"]}'::jsonb,
    '[]'::jsonb
  ),
  (
    gen_random_uuid(),
    'Interpersonal Therapy',
    'IPT',
    'Addresses current interpersonal problems and their connection to mood disorders.',
    'relational',
    12,
    '["Problem Identification", "Grief Work", "Dispute Resolution", "Maintenance"]'::jsonb,
    '["Communication Analysis", "Role Exploration", "Grief Processing", "Interpersonal Problem Solving"]'::jsonb,
    '{"efficacy": "Strong", "evidence_level": "A", "conditions": ["Major Depression", "Bipolar Disorder", "Eating Disorders"]}'::jsonb,
    '[]'::jsonb
  ),
  (
    gen_random_uuid(),
    'Motivational Interviewing',
    'MI',
    'Collaborative approach that focuses on exploring ambivalence about change through empathic listening.',
    'relational',
    8,
    '["Building Rapport", "Exploring Ambivalence", "Developing Change Talk", "Commitment to Change"]'::jsonb,
    '["Open Questions", "Affirmations", "Reflective Listening", "Summaries"]'::jsonb,
    '{"efficacy": "Strong", "evidence_level": "A", "conditions": ["Substance Abuse", "Behavior Change", "Diabetes Management"]}'::jsonb,
    '[]'::jsonb
  ),
  (
    gen_random_uuid(),
    'Mindfulness-Based Cognitive Therapy',
    'MBCT',
    'Combines mindfulness meditation with cognitive therapy principles to prevent relapse.',
    'mindfulness',
    8,
    '["Mindfulness Foundation", "Awareness of Thoughts", "Decentering", "Relapse Prevention"]'::jsonb,
    '["Sitting Meditation", "Body Scan", "Mindful Movement", "Mindful Eating"]'::jsonb,
    '{"efficacy": "Strong", "evidence_level": "A", "conditions": ["Depression Relapse Prevention", "Anxiety", "Chronic Pain"]}'::jsonb,
    '[]'::jsonb
  ),
  (
    gen_random_uuid(),
    'Schema Therapy',
    'ST',
    'Integrative approach that addresses core emotional and relational patterns established in early life.',
    'cognitive-behavioral',
    16,
    '["Assessment", "Psychoeducation", "Schema Work", "Behavioral Change"]'::jsonb,
    '["Limited Reparenting", "Imagery Rescripting", "Experiential Techniques", "Behavioral Assignments"]'::jsonb,
    '{"efficacy": "Strong", "evidence_level": "A", "conditions": ["Personality Disorders", "Chronic Depression", "Trauma"]}'::jsonb,
    '[]'::jsonb
  ),
  (
    gen_random_uuid(),
    'Eye Movement Desensitization and Reprocessing',
    'EMDR',
    'Uses bilateral eye movements to process traumatic memories and reduce emotional distress.',
    'trauma',
    12,
    '["History Taking", "Preparation", "Assessment", "Desensitization", "Installation", "Closure"]'::jsonb,
    '["Bilateral Stimulation", "Memory Reprocessing", "Resource Installation"]'::jsonb,
    '{"efficacy": "Strong", "evidence_level": "A", "conditions": ["PTSD", "Trauma", "Anxiety"]}'::jsonb,
    '["Active psychosis", "Recent substance use", "Uncontrolled seizures"]'::jsonb
  ),
  (
    gen_random_uuid(),
    'Supportive Psychotherapy',
    'SUP',
    'Non-specific supportive interventions that provide empathy, validation, and practical guidance.',
    'relational',
    12,
    '["Engagement", "Support Building", "Adaptive Functioning", "Integration"]'::jsonb,
    '["Empathic Reflection", "Validation", "Psychoeducation", "Practical Guidance"]'::jsonb,
    '{"efficacy": "Moderate", "evidence_level": "B", "conditions": ["General Mental Health", "Crisis Support"]}'::jsonb,
    '[]'::jsonb
  ),
  (
    gen_random_uuid(),
    'Transference-Focused Psychotherapy',
    'TFP',
    'Addresses personality pathology through focused attention on transference patterns in the therapeutic relationship.',
    'psychodynamic',
    24,
    '["Engagement", "Transference Analysis", "Personality Change"]'::jsonb,
    '["Transference Exploration", "Interpretive Work", "Mentalization", "Clarification"]'::jsonb,
    '{"efficacy": "Strong", "evidence_level": "A", "conditions": ["Borderline Personality Disorder", "Severe Personality Pathology"]}'::jsonb,
    '["Inability to tolerate high-structure environment"]'::jsonb
  ),
  (
    gen_random_uuid(),
    'Existential Therapy',
    'EXI',
    'Explores themes of freedom, responsibility, meaning, and authentic living.',
    'existential',
    12,
    '["Awareness of Existential Issues", "Exploration of Authenticity", "Meaning-Making", "Integration"]'::jsonb,
    '["Phenomenological Inquiry", "Responsibility Exploration", "Freedom and Choice Work"]'::jsonb,
    '{"efficacy": "Moderate", "evidence_level": "C", "conditions": ["Existential Concerns", "Life Transitions", "Meaning Seeking"]}'::jsonb,
    '[]'::jsonb
  );

-- Insert modality combinations (frequently used integrations)
INSERT INTO modality_combinations (
  primary_modality_id, secondary_modality_id, integration_description, efficacy_score, condition_tags
)
SELECT
  (SELECT modality_id FROM therapy_modalities WHERE name = 'Cognitive Behavioral Therapy'),
  (SELECT modality_id FROM therapy_modalities WHERE name = 'Motivational Interviewing'),
  'CBT for addressing thoughts/behaviors + MI for exploring ambivalence; highly effective for substance use and behavioral change',
  0.95,
  '["Substance Use Disorder", "Behavior Change Resistance", "Dual Diagnosis"]'::jsonb
WHERE EXISTS (SELECT 1 FROM therapy_modalities WHERE name = 'Cognitive Behavioral Therapy')
  AND EXISTS (SELECT 1 FROM therapy_modalities WHERE name = 'Motivational Interviewing');

-- Sample clinic
INSERT INTO clinics (
  clinic_id, name, email, phone, license_number, status
) VALUES
  (gen_random_uuid(), 'Center for Mental Wellness', 'contact@mentalwellness.com', '555-0100', 'MH-001', 'active');

-- Note: More seed data will be added as the system develops
-- This provides a foundation for therapy modalities and integrations