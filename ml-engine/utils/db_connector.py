"""
Database Connector Utility

Manages connections to PostgreSQL for therapy data and recommendations
"""

import asyncio
import logging
from typing import List, Dict, Optional
import psycopg2
from psycopg2.pool import SimpleConnectionPool

logger = logging.getLogger(__name__)


class DatabaseConnector:
    """
    Manages database connections and queries
    """

    def __init__(
        self,
        host: str,
        port: int,
        database: str,
        user: str,
        password: str,
        min_conn: int = 2,
        max_conn: int = 10
    ):
        """
        Initialize database connector

        Args:
            host: PostgreSQL host
            port: PostgreSQL port
            database: Database name
            user: Database user
            password: Database password
            min_conn: Minimum connection pool size
            max_conn: Maximum connection pool size
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password

        # Create connection string
        self.conn_string = (
            f"host={host} port={port} database={database} "
            f"user={user} password={password}"
        )

        # Create connection pool
        try:
            self.pool = SimpleConnectionPool(
                min_conn,
                max_conn,
                self.conn_string
            )
            logger.info(f"Database connection pool created ({min_conn}-{max_conn} connections)")
        except Exception as e:
            logger.error(f"Error creating connection pool: {e}")
            self.pool = None

    def query(self, sql: str, params: Optional[tuple] = None) -> List[Dict]:
        """
        Execute SELECT query

        Args:
            sql: SQL query string
            params: Query parameters for prepared statement

        Returns:
            List of result rows as dictionaries
        """
        try:
            conn = self.pool.getconn()
            try:
                cursor = conn.cursor()
                cursor.execute(sql, params or ())

                # Get column names
                columns = [desc[0] for desc in cursor.description]

                # Fetch results as list of dicts
                rows = []
                for row in cursor.fetchall():
                    rows.append(dict(zip(columns, row)))

                cursor.close()
                return rows

            finally:
                self.pool.putconn(conn)

        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return []

    def execute(self, sql: str, params: Optional[tuple] = None) -> int:
        """
        Execute INSERT/UPDATE/DELETE query

        Args:
            sql: SQL query string
            params: Query parameters for prepared statement

        Returns:
            Number of affected rows
        """
        try:
            conn = self.pool.getconn()
            try:
                cursor = conn.cursor()
                cursor.execute(sql, params or ())
                rowcount = cursor.rowcount

                conn.commit()
                cursor.close()
                return rowcount

            except Exception as e:
                conn.rollback()
                raise e
            finally:
                self.pool.putconn(conn)

        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return 0

    def get_therapy_modalities(self) -> List[Dict]:
        """Get all therapy modalities from database"""
        sql = """
            SELECT modality_id, name, abbreviation, description,
                   evidence_base, typical_duration, key_techniques
            FROM therapy_modalities
            ORDER BY name
        """
        return self.query(sql)

    def get_modality_combinations(self) -> List[Dict]:
        """Get evidence-based modality combinations"""
        sql = """
            SELECT combination_id, modality1_id, modality2_id,
                   combination_name, efficacy_score, use_cases
            FROM modality_combinations
            ORDER BY efficacy_score DESC
        """
        return self.query(sql)

    def get_assessment_scales(self) -> List[Dict]:
        """Get all assessment scales from database"""
        sql = """
            SELECT scale_id, name, abbreviation, category,
                   score_range, interpretation_guide,
                   sensitivity, specificity
            FROM assessment_scales
            ORDER BY category, name
        """
        return self.query(sql)

    def get_patient_history(self, patient_id: str) -> Dict:
        """
        Get patient history for outcome prediction

        Args:
            patient_id: Patient ID

        Returns:
            Patient history dict with previous modalities and outcomes
        """
        try:
            # Get patient demographics
            patient_sql = """
                SELECT patient_id, demographics, clinical_profile
                FROM unified_patient_profiles
                WHERE patient_id = %s
            """
            patient = self.query(patient_sql, (patient_id,))

            if not patient:
                return {}

            patient_data = patient[0]

            # Get previous sessions and outcomes
            sessions_sql = """
                SELECT ts.session_id, ts.therapy_modality_id, ts.session_date,
                       so.symptom_severity_change, so.patient_satisfaction
                FROM therapy_sessions ts
                LEFT JOIN session_outcomes so ON ts.session_id = so.session_id
                WHERE ts.patient_id = %s
                ORDER BY ts.session_date DESC
                LIMIT 10
            """
            sessions = self.query(sessions_sql, (patient_id,))

            return {
                "patient": patient_data,
                "previous_sessions": sessions,
            }

        except Exception as e:
            logger.error(f"Error getting patient history: {e}")
            return {}

    def save_recommendation(self, recommendation_data: Dict) -> bool:
        """
        Save recommendation to database

        Args:
            recommendation_data: Dict with recommendation details

        Returns:
            True if saved successfully
        """
        try:
            sql = """
                INSERT INTO recommendations
                (scenario_id, patient_id, recommended_modalities,
                 confidence_score, generated_at, model_version)
                VALUES (%s, %s, %s, %s, NOW(), %s)
            """
            modalities_json = str(recommendation_data.get("modalities", []))

            self.execute(
                sql,
                (
                    recommendation_data.get("scenario_id"),
                    recommendation_data.get("patient_id"),
                    modalities_json,
                    recommendation_data.get("confidence_score", 0.5),
                    "phase2_v1"
                )
            )
            logger.info(f"Recommendation saved for scenario: {recommendation_data.get('scenario_id')}")
            return True

        except Exception as e:
            logger.error(f"Error saving recommendation: {e}")
            return False

    def close(self):
        """Close all connections in pool"""
        try:
            if self.pool:
                self.pool.closeall()
                logger.info("Database connection pool closed")
        except Exception as e:
            logger.error(f"Error closing connection pool: {e}")
