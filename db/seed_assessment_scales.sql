-- ============================================================================
-- ASSESSMENT SCALES SEED DATA
-- ============================================================================
-- Comprehensive collection of psychiatric and psychological assessment scales
-- Used for symptom measurement, diagnostic screening, and treatment monitoring

-- DEPRESSION ASSESSMENTS
INSERT INTO assessment_scales (name, abbreviation, description, category, num_items, score_range, interpretation, administration_time_minutes, evidence_base, use_cases, languages_available, copyright_info, reference_links)
VALUES
  (
    'Patient Health Questionnaire-9',
    'PHQ-9',
    'Brief 9-item self-report measure of depression severity. Screens for depression and monitors severity over time.',
    'depression',
    9,
    '{"min": 0, "max": 27}'::jsonb,
    '{"0-4": "minimal", "5-9": "mild", "10-14": "moderate", "15-19": "moderately severe", "20-27": "severe"}'::jsonb,
    3,
    '{"sensitivity": "88%", "specificity": "88%", "internal_consistency": "0.89"}'::jsonb,
    '["Major Depressive Disorder", "Dysthymia", "Treatment monitoring"]'::jsonb,
    '["English", "Spanish", "Chinese", "German", "French"]'::jsonb,
    'Public domain. Developed by Pfizer. Freely available for clinical use.',
    '{"publication": "JAMA 1999", "link": "https://www.phqscreeners.com"}'::jsonb
  ),
  (
    'Beck Depression Inventory-II',
    'BDI-II',
    '21-item self-report measure assessing cognitive, emotional, and physical symptoms of depression.',
    'depression',
    21,
    '{"min": 0, "max": 63}'::jsonb,
    '{"0-13": "minimal", "14-19": "mild", "20-28": "moderate", "29-63": "severe"}'::jsonb,
    5,
    '{"sensitivity": "94%", "specificity": "95%", "internal_consistency": "0.92"}'::jsonb,
    '["Major Depressive Disorder", "Treatment monitoring", "Severity assessment"]'::jsonb,
    '["English", "Spanish", "French", "German", "Italian"]'::jsonb,
    'Copyrighted by Psychological Assessment Resources (PAR). Licensing required.',
    '{"link": "https://www.parinc.com"}'::jsonb
  ),
  (
    'Montgomery-Åsberg Depression Rating Scale',
    'MADRS',
    '10-item clinician-rated scale measuring depression severity. Gold standard for antidepressant trials.',
    'depression',
    10,
    '{"min": 0, "max": 60}'::jsonb,
    '{"0-6": "normal", "7-19": "mild", "20-34": "moderate", "35-60": "severe"}'::jsonb,
    8,
    '{"inter-rater_reliability": "0.97", "sensitivity": "92%", "specificity": "89%"}'::jsonb,
    '["Major Depressive Disorder", "Treatment trials", "Clinical monitoring"]'::jsonb,
    '["English", "Swedish", "German", "Spanish"]'::jsonb,
    'Public domain. Freely available.',
    '{"publication": "BJPSYCH 1979", "link": "https://en.wikipedia.org/wiki/Montgomery%E2%80%93%C3%85sberg_Depression_Rating_Scale"}'::jsonb
  );

-- ANXIETY ASSESSMENTS
INSERT INTO assessment_scales (name, abbreviation, description, category, num_items, score_range, interpretation, administration_time_minutes, evidence_base, use_cases, languages_available, copyright_info, reference_links)
VALUES
  (
    'Generalized Anxiety Disorder-7',
    'GAD-7',
    'Brief 7-item self-report screening tool for generalized anxiety disorder. Fast and reliable.',
    'anxiety',
    7,
    '{"min": 0, "max": 21}'::jsonb,
    '{"0-4": "minimal", "5-9": "mild", "10-14": "moderate", "15-21": "severe"}'::jsonb,
    2,
    '{"sensitivity": "89%", "specificity": "97%", "internal_consistency": "0.92"}'::jsonb,
    '["Generalized Anxiety Disorder", "Anxiety screening", "Treatment monitoring"]'::jsonb,
    '["English", "Spanish", "French", "German", "Dutch"]'::jsonb,
    'Public domain. Developed by Pfizer.',
    '{"publication": "ARCH INTERN MED 2006", "link": "https://www.phqscreeners.com"}'::jsonb
  ),
  (
    'Beck Anxiety Inventory',
    'BAI',
    '21-item self-report measure of anxiety symptoms in adolescents and adults.',
    'anxiety',
    21,
    '{"min": 0, "max": 63}'::jsonb,
    '{"0-21": "low", "22-35": "moderate", "36-63": "high"}'::jsonb,
    5,
    '{"internal_consistency": "0.92", "sensitivity": "95%", "specificity": "94%"}'::jsonb,
    '["Generalized Anxiety Disorder", "Panic Disorder", "Social Anxiety", "PTSD"]'::jsonb,
    '["English", "Spanish", "French", "Dutch"]'::jsonb,
    'Copyrighted by Psychological Assessment Resources (PAR).',
    '{"link": "https://www.parinc.com"}'::jsonb
  ),
  (
    'Hamilton Anxiety Rating Scale',
    'HAM-A',
    '14-item clinician-administered scale measuring anxiety severity. Gold standard for anxiety treatment trials.',
    'anxiety',
    14,
    '{"min": 0, "max": 56}'::jsonb,
    '{"0-5": "normal", "6-14": "mild", "15-27": "moderate", "28-56": "severe"}'::jsonb,
    10,
    '{"inter-rater_reliability": "0.84", "test_retest": "0.85"}'::jsonb,
    '["Generalized Anxiety Disorder", "Panic Disorder", "Treatment trials"]'::jsonb,
    '["English", "German", "French"]'::jsonb,
    'Public domain. Freely available.',
    '{"publication": "PSYCHIATRY RESEARCH 1959"}'::jsonb
  );

-- PTSD & TRAUMA ASSESSMENTS
INSERT INTO assessment_scales (name, abbreviation, description, category, num_items, score_range, interpretation, administration_time_minutes, evidence_base, use_cases, languages_available, copyright_info, reference_links)
VALUES
  (
    'PTSD Checklist for DSM-5',
    'PCL-5',
    '20-item self-report measure of post-traumatic stress disorder symptoms. Maps to DSM-5 criteria.',
    'ptsd',
    20,
    '{"min": 0, "max": 80}'::jsonb,
    '{"0-14": "minimal", "15-28": "mild", "29-43": "moderate", "44-60": "severe", "61-80": "very severe"}'::jsonb,
    5,
    '{"sensitivity": "94%", "specificity": "97%", "internal_consistency": "0.94"}'::jsonb,
    '["PTSD", "Trauma screening", "Treatment monitoring"]'::jsonb,
    '["English", "Spanish", "French", "German", "Dutch", "Chinese"]'::jsonb,
    'Public domain. Developed by the National Center for PTSD.',
    '{"link": "https://www.ptsd.va.gov/professional/assessment/adult-sr/ptsd-checklist.asp"}'::jsonb
  ),
  (
    'Clinician-Administered PTSD Scale for DSM-5',
    'CAPS-5',
    '30-item clinician-administered gold standard measure of PTSD severity.',
    'ptsd',
    30,
    '{"min": 0, "max": 136}'::jsonb,
    '{"0-13": "below threshold", "14-36": "mild", "37-72": "moderate", "73-136": "severe"}'::jsonb,
    45,
    '{"inter-rater_reliability": "0.95", "sensitivity": "92%", "specificity": "98%"}'::jsonb,
    '["PTSD diagnosis", "Severity assessment", "Treatment trials"]'::jsonb,
    '["English", "German", "French"]'::jsonb,
    'Public domain. Developed by the National Center for PTSD.',
    '{"link": "https://www.ptsd.va.gov/professional/assessment/adult-sr/caps.asp"}'::jsonb
  ),
  (
    'Impact of Event Scale-Revised',
    'IES-R',
    '22-item self-report measure of post-traumatic stress from specific events.',
    'ptsd',
    22,
    '{"min": 0, "max": 88}'::jsonb,
    '{"0-8": "normal", "9-25": "mild", "26-43": "moderate", "44-88": "severe"}'::jsonb,
    5,
    '{"internal_consistency": "0.96", "test_retest": "0.94"}'::jsonb,
    '["PTSD", "Trauma assessment", "Specific event impact"]'::jsonb,
    '["English", "Spanish", "German", "Italian"]'::jsonb,
    'Public domain. Developed by Weiss & Marmar.',
    '{"publication": "J CONSULT CLIN PSYCHOL 1997"}'::jsonb
  );

-- SUBSTANCE USE ASSESSMENTS
INSERT INTO assessment_scales (name, abbreviation, description, category, num_items, score_range, interpretation, administration_time_minutes, evidence_base, use_cases, languages_available, copyright_info, reference_links)
VALUES
  (
    'AUDIT: Alcohol Use Disorders Identification Test',
    'AUDIT',
    '10-item screening tool for harmful alcohol use and alcohol dependence.',
    'substance_use',
    10,
    '{"min": 0, "max": 40}'::jsonb,
    '{"0-7": "abstainer/low-risk", "8-15": "increasing risk", "16-19": "higher risk", "20-40": "possible alcohol dependence"}'::jsonb,
    3,
    '{"sensitivity": "92%", "specificity": "94%"}'::jsonb,
    '["Alcohol Use Disorder", "Screening", "Risk assessment"]'::jsonb,
    '["English", "Spanish", "French", "German", "Dutch", "Chinese"]'::jsonb,
    'Public domain. Developed by WHO.',
    '{"link": "https://www.who.int/publications/i/item/WHO-MSD-MSB-89.4"}'::jsonb
  ),
  (
    'DAST-10: Drug Abuse Screening Test',
    'DAST-10',
    '10-item screening tool for problematic drug use behavior.',
    'substance_use',
    10,
    '{"min": 0, "max": 10}'::jsonb,
    '{"0-2": "no problem", "3-5": "mild", "6-8": "moderate", "9-10": "substantial"}'::jsonb,
    2,
    '{"sensitivity": "94%", "specificity": "87%"}'::jsonb,
    '["Substance Use Disorder", "Drug screening", "Severity assessment"]'::jsonb,
    '["English", "Spanish", "French"]'::jsonb,
    'Public domain. Developed by Skinner.',
    '{"link": "https://www.samhsa.gov"}'::jsonb
  ),
  (
    'CAGE Questionnaire',
    'CAGE',
    '4-item brief screening tool for alcohol misuse and dependence.',
    'substance_use',
    4,
    '{"min": 0, "max": 4}'::jsonb,
    '{"0": "unlikely alcohol problem", "1": "possible problem", "2-4": "likely alcohol problem"}'::jsonb,
    1,
    '{"sensitivity": "89%", "specificity": "79%"}'::jsonb,
    '["Alcohol Use Disorder", "Brief screening", "Primary care"]'::jsonb,
    '["English", "Spanish"]'::jsonb,
    'Public domain. Developed by Ewing.',
    '{"publication": "JAMA 1984"}'::jsonb
  );

-- SLEEP ASSESSMENTS
INSERT INTO assessment_scales (name, abbreviation, description, category, num_items, score_range, interpretation, administration_time_minutes, evidence_base, use_cases, languages_available, copyright_info, reference_links)
VALUES
  (
    'Pittsburgh Sleep Quality Index',
    'PSQI',
    '19-item self-report measure of sleep quality. Comprehensive assessment of sleep disturbance.',
    'sleep',
    19,
    '{"min": 0, "max": 21}'::jsonb,
    '{"0-5": "good sleep quality", "6-21": "poor sleep quality"}'::jsonb,
    5,
    '{"sensitivity": "89%", "specificity": "86%", "internal_consistency": "0.83"}'::jsonb,
    '["Sleep disorders", "Insomnia", "Sleep monitoring"]'::jsonb,
    '["English", "Spanish", "German", "French"]'::jsonb,
    'Public domain. Developed by Buysse et al.',
    '{"publication": "PSYCHIATRY RES 1989", "link": "https://sleep.pitt.edu"}'::jsonb
  );

-- GENERAL FUNCTIONING & DISABILITY
INSERT INTO assessment_scales (name, abbreviation, description, category, num_items, score_range, interpretation, administration_time_minutes, evidence_base, use_cases, languages_available, copyright_info, reference_links)
VALUES
  (
    'Global Assessment of Functioning',
    'GAF',
    '0-100 clinician-rated scale measuring psychological, social, and occupational functioning.',
    'functioning',
    1,
    '{"min": 0, "max": 100}'::jsonb,
    '{"91-100": "superior", "81-90": "good", "71-80": "mild symptoms", "61-70": "moderate symptoms", "51-60": "moderate difficulty", "41-50": "serious symptoms", "31-40": "major impairment", "21-30": "major impairment with inability", "11-20": "minimal impairment", "1-10": "persistent danger"}'::jsonb,
    2,
    '{"inter-rater_reliability": "0.85"}'::jsonb,
    '["General assessment", "Treatment monitoring", "Functional status"]'::jsonb,
    '["English", "German", "French"]'::jsonb,
    'Copyrighted. Part of DSM-5.',
    '{"link": "https://www.psychiatry.org"}'::jsonb
  ),
  (
    'World Health Organization Disability Assessment Schedule 2.0',
    'WHODAS 2.0',
    '36-item assessment of disability and functional limitations across 6 domains.',
    'functioning',
    36,
    '{"min": 0, "max": 100}'::jsonb,
    '{"0-4%": "none", "5-24%": "mild", "25-49%": "moderate", "50-95%": "severe", "96-100%": "complete"}'::jsonb,
    20,
    '{"test_retest": "0.98", "sensitivity": "0.94"}'::jsonb,
    '["Disability assessment", "Functional impairment", "Multi-domain evaluation"]'::jsonb,
    '["English", "Spanish", "French", "German", "Chinese", "Arabic"]'::jsonb,
    'Public domain. Developed by WHO.',
    '{"link": "https://www.who.int/standards/classifications/related-health-conditions/whodas-2-0"}'::jsonb
  );

-- MANIA & BIPOLAR ASSESSMENTS
INSERT INTO assessment_scales (name, abbreviation, description, category, num_items, score_range, interpretation, administration_time_minutes, evidence_base, use_cases, languages_available, copyright_info, reference_links)
VALUES
  (
    'Young Mania Rating Scale',
    'YMRS',
    '11-item clinician-administered scale measuring manic symptoms severity.',
    'mania',
    11,
    '{"min": 0, "max": 60}'::jsonb,
    '{"0-5": "normal", "6-19": "mild to moderate", "20-35": "moderate to severe", "36-60": "severe"}'::jsonb,
    10,
    '{"inter-rater_reliability": "0.93", "internal_consistency": "0.93"}'::jsonb,
    '["Bipolar Disorder", "Mania assessment", "Treatment monitoring"]'::jsonb,
    '["English", "German", "Spanish"]'::jsonb,
    'Public domain. Developed by Young et al.',
    '{"publication": "J AFFECT DISORD 1987"}'::jsonb
  );

-- PSYCHOSIS ASSESSMENTS
INSERT INTO assessment_scales (name, abbreviation, description, category, num_items, score_range, interpretation, administration_time_minutes, evidence_base, use_cases, languages_available, copyright_info, reference_links)
VALUES
  (
    'Positive and Negative Syndrome Scale',
    'PANSS',
    '30-item clinician-rated scale measuring positive, negative, and general psychopathology symptoms.',
    'psychosis',
    30,
    '{"min": 30, "max": 210}'::jsonb,
    '{"30-54": "normal", "55-87": "mild", "88-140": "moderate", "141-210": "severe"}'::jsonb,
    40,
    '{"inter-rater_reliability": "0.87", "sensitivity": "97%", "specificity": "95%"}'::jsonb,
    '["Schizophrenia", "Psychosis", "Antipsychotic efficacy trials"]'::jsonb,
    '["English", "German", "Spanish", "French"]'::jsonb,
    'Copyrighted. Licensing required for some versions.',
    '{"publication": "SCHIZOPHR BULL 1987"}'::jsonb
  );

-- AGGRESSION & BEHAVIOR ASSESSMENTS
INSERT INTO assessment_scales (name, abbreviation, description, category, num_items, score_range, interpretation, administration_time_minutes, evidence_base, use_cases, languages_available, copyright_info, reference_links)
VALUES
  (
    'Overt Aggression Scale',
    'OAS',
    'Observer-rated scale measuring frequency and severity of aggressive behavior.',
    'aggression',
    4,
    '{"min": 0, "max": variable}'::jsonb,
    '{"0": "no aggression", "1": "verbal aggression", "2": "physical against objects", "3": "physical against self", "4": "physical against others"}'::jsonb,
    15,
    '{"inter-rater_reliability": "0.94"}'::jsonb,
    '["Aggression monitoring", "Behavioral disturbance", "Violence risk"]'::jsonb,
    '["English", "German"]'::jsonb,
    'Public domain. Developed by Yudofsky et al.',
    '{"publication": "AM J PSYCHIATRY 1986"}'::jsonb
  );

-- GENERAL PSYCHOPATHOLOGY
INSERT INTO assessment_scales (name, abbreviation, description, category, num_items, score_range, interpretation, administration_time_minutes, evidence_base, use_cases, languages_available, copyright_info, reference_links)
VALUES
  (
    'Clinical Global Impression',
    'CGI',
    'Brief clinician-rated scale of overall severity and improvement.',
    'general',
    2,
    '{"min": 1, "max": 7}'::jsonb,
    '{"1": "normal", "2": "borderline ill", "3": "mildly ill", "4": "moderately ill", "5": "markedly ill", "6": "severely ill", "7": "extremely ill"}'::jsonb,
    1,
    '{"test_retest": "0.81"}'::jsonb,
    '["General severity assessment", "Treatment monitoring", "Clinical trials"]'::jsonb,
    '["English", "German", "Spanish"]'::jsonb,
    'Public domain. Developed by NIMH.',
    '{"publication": "PSYCHOPHARMACOL BULL 1976"}'::jsonb
  );
