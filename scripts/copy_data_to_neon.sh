#!/usr/bin/env bash
set -euo pipefail

# Load .env from repo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: .env file not found at $ENV_FILE"
  exit 1
fi

set -a
# shellcheck source=/dev/null
source "$ENV_FILE"
set +a

if [[ -z "${AWS_DB_URL:-}" ]]; then
  echo "ERROR: AWS_DB_URL is not set in .env"
  exit 1
fi

if [[ -z "${NEON_DB_URL_DIRECT:-}" ]]; then
  echo "ERROR: NEON_DB_URL_DIRECT is not set in .env"
  exit 1
fi

echo "Source : $AWS_DB_URL"
echo "Target : $NEON_DB_URL_DIRECT"
echo ""
echo "This will copy all data from the source database into Neon."
echo "Existing rows in Neon with conflicting primary keys will cause errors."
read -rp "Continue? (y/N) " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
  echo "Aborted."
  exit 0
fi

echo ""
echo "Dumping data from source..."
pg_dump \
  --data-only \
  --no-owner \
  --no-privileges \
  --disable-triggers \
  --inserts \
  --on-conflict-do-nothing \
  --exclude-table=alembic_version \
  "$AWS_DB_URL" | psql "$NEON_DB_URL_DIRECT"

echo ""
echo "Done."
