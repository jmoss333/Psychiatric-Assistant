#!/bin/bash

# Database Verification Script
# Checks if all required tables and data are properly set up

echo "═════════════════════════════════════════════════════"
echo "Smart Communicator Database Verification"
echo "═════════════════════════════════════════════════════"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Database configuration
DB_USER=${DB_USER:-"postgres"}
DB_HOST=${DB_HOST:-"localhost"}
DB_PORT=${DB_PORT:-"5432"}
DB_NAME=${DB_NAME:-"smart_communicator"}

echo "Database Configuration:"
echo "  User: $DB_USER"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  Database: $DB_NAME"
echo ""

# Function to check if database exists
check_database_exists() {
  echo -n "Checking if database exists... "
  if psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -l | grep -q "$DB_NAME"; then
    echo -e "${GREEN}✓${NC}"
    return 0
  else
    echo -e "${RED}✗${NC}"
    echo "  Create with: createdb $DB_NAME"
    return 1
  fi
}

# Function to check if table exists
check_table() {
  local table=$1
  if psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c "\dt $table" | grep -q "$table"; then
    echo -e "  ${GREEN}✓${NC} $table"
    return 0
  else
    echo -e "  ${RED}✗${NC} $table"
    return 1
  fi
}

# Function to count rows in table
count_rows() {
  local table=$1
  local count=$(psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM $table;")
  echo "      ├─ Rows: $count"
}

# Check database exists
if ! check_database_exists; then
  exit 1
fi

echo ""
echo "Checking Core Tables:"
tables=(
  "clinics"
  "therapists"
  "sessions_tokens"
  "unified_patient_profiles"
  "therapy_modalities"
  "modality_combinations"
  "clinical_scenarios"
  "recommendations"
  "therapy_sessions"
  "session_outcomes"
  "long_term_outcomes"
  "integrated_analytics"
)

all_tables_exist=true
for table in "${tables[@]}"; do
  if ! check_table "$table"; then
    all_tables_exist=false
  else
    count_rows "$table"
  fi
done

echo ""
echo "Checking Reference Data:"
echo -n "  Therapy Modalities: "
modality_count=$(psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM therapy_modalities;")
if [ "$modality_count" -gt 0 ]; then
  echo -e "${GREEN}$modality_count${NC}"
else
  echo -e "${RED}0 (should seed with seed.sql)${NC}"
fi

echo -n "  Modality Combinations: "
combination_count=$(psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM modality_combinations;")
if [ "$combination_count" -gt 0 ]; then
  echo -e "${GREEN}$combination_count${NC}"
else
  echo -e "${YELLOW}0${NC}"
fi

echo -n "  Clinics: "
clinic_count=$(psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM clinics;")
if [ "$clinic_count" -gt 0 ]; then
  echo -e "${GREEN}$clinic_count${NC}"
else
  echo -e "${YELLOW}0 (create during testing)${NC}"
fi

echo ""
echo "Checking Indexes:"
indexes=$(psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public';")
echo "  Total Indexes: ${GREEN}$indexes${NC}"

echo ""
echo "Checking Schema Size:"
size=$(psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT pg_size_pretty(pg_database_size('$DB_NAME'));")
echo "  Database Size: ${GREEN}$size${NC}"

echo ""
echo "═════════════════════════════════════════════════════"

if [ "$all_tables_exist" = true ] && [ "$modality_count" -gt 0 ]; then
  echo -e "${GREEN}✓ Database is ready for testing${NC}"
  echo ""
  echo "Next steps:"
  echo "  1. Start backend: npm run dev"
  echo "  2. Run tests: node test-runner.js"
  echo ""
  exit 0
else
  echo -e "${RED}✗ Database setup incomplete${NC}"
  echo ""
  echo "To complete setup:"
  echo "  1. Create schema: psql -U postgres -d $DB_NAME -f ../db/schema.sql"
  echo "  2. Seed data: psql -U postgres -d $DB_NAME -f ../db/seed.sql"
  echo "  3. Run verification again: ./verify-db.sh"
  echo ""
  exit 1
fi
