"""
Training Data Extraction Script

Extracts clinical data from Smart Communicator database
for ML model training (Phase 2B)

Usage:
    python extract_training_data.py --output data/training_data.csv
"""

import argparse
import logging
import pandas as pd
import json
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_connector import DatabaseConnector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_training_data(db_connector, output_file: str = None):
    """
    Extract training data from database

    Collects:
    1. Clinical scenarios with clinical metadata
    2. Recommended modalities
    3. Session outcomes (if available)
    4. Assessment scale measurements

    Args:
        db_connector: DatabaseConnector instance
        output_file: Output CSV file path
    """

    logger.info("Starting data extraction...")

    # Query clinical scenarios
    scenarios_sql = """
        SELECT
            cs.scenario_id,
            cs.patient_id,
            cs.clinic_id,
            cs.scenario_type,
            cs.presenting_problems,
            cs.dsm5_codes,
            cs.assessment_scales,
            cs.psychosocial_stressors,
            cs.protective_factors,
            cs.created_at,
            up.demographics,
            up.clinical_profile,
            COALESCE(ts.therapy_modality_id, '') as recommended_modality,
            COALESCE(so.symptom_severity_change, 0) as outcome_score,
            COALESCE(so.patient_satisfaction, 0) as satisfaction_score
        FROM clinical_scenarios cs
        LEFT JOIN unified_patient_profiles up ON cs.patient_id = up.patient_id
        LEFT JOIN therapy_sessions ts ON cs.scenario_id = ts.scenario_id
        LEFT JOIN session_outcomes so ON ts.session_id = so.session_id
        WHERE cs.created_at >= DATE_TRUNC('month', NOW() - INTERVAL '12 months')
        ORDER BY cs.created_at DESC
    """

    logger.info("Extracting scenarios from database...")
    rows = db_connector.query(scenarios_sql)
    logger.info(f"Found {len(rows)} clinical scenarios")

    if not rows:
        logger.warning("No data found in database")
        return None

    # Prepare training data
    training_data = []

    for row in rows:
        try:
            # Parse JSON fields
            presenting_problems = json.loads(row.get("presenting_problems", "[]"))
            dsm5_codes = json.loads(row.get("dsm5_codes", "[]"))
            assessment_scales = json.loads(row.get("assessment_scales", "{}"))
            stressors = json.loads(row.get("psychosocial_stressors", "[]"))
            protective_factors = json.loads(row.get("protective_factors", "[]"))

            # Extract features
            training_row = {
                # IDs
                "scenario_id": row["scenario_id"],
                "patient_id": row["patient_id"],

                # Clinical data
                "num_presenting_problems": len(presenting_problems),
                "num_dsm5_codes": len(dsm5_codes),
                "num_stressors": len(stressors),
                "num_protective_factors": len(protective_factors),

                # Assessment scores (average)
                "avg_assessment_score": (
                    sum(assessment_scales.values()) / len(assessment_scales)
                    if assessment_scales
                    else 0
                ),

                # Outcome (target variable)
                "recommended_modality": row.get("recommended_modality", ""),
                "outcome_score": row.get("outcome_score", 0),
                "satisfaction_score": row.get("satisfaction_score", 0),

                # Timestamp
                "created_at": row["created_at"],
            }

            training_data.append(training_row)

        except Exception as e:
            logger.error(f"Error processing scenario {row.get('scenario_id')}: {e}")
            continue

    # Convert to DataFrame
    df = pd.DataFrame(training_data)

    # Save to CSV
    if output_file:
        df.to_csv(output_file, index=False)
        logger.info(f"Training data saved to {output_file}")
        logger.info(f"Total rows: {len(df)}")
        logger.info(f"Columns: {list(df.columns)}")
    else:
        logger.info(f"Generated {len(df)} training samples")

    return df


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Extract training data from Smart Communicator"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/training_data.csv",
        help="Output CSV file path"
    )
    parser.add_argument(
        "--db-host",
        type=str,
        default="localhost",
        help="Database host"
    )
    parser.add_argument(
        "--db-port",
        type=int,
        default=5432,
        help="Database port"
    )
    parser.add_argument(
        "--db-name",
        type=str,
        default="smart_communicator",
        help="Database name"
    )
    parser.add_argument(
        "--db-user",
        type=str,
        default="postgres",
        help="Database user"
    )
    parser.add_argument(
        "--db-password",
        type=str,
        default="",
        help="Database password"
    )

    args = parser.parse_args()

    # Create database connector
    db_connector = DatabaseConnector(
        host=args.db_host,
        port=args.db_port,
        database=args.db_name,
        user=args.db_user,
        password=args.db_password
    )

    # Extract data
    df = extract_training_data(db_connector, args.output)

    if df is not None:
        logger.info("Data extraction completed successfully")
    else:
        logger.error("Data extraction failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
