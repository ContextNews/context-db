#!/usr/bin/env bash
set -euo pipefail

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

TABLES=(
  articles
  article_clusters
  article_cluster_articles
  article_embeddings
  article_entity_mentions
  article_entities_resolved
  article_topics
  topics
  stories
  story_articles
  story_entities
  story_edges
  story_topics
  kb_entities
  kb_entity_aliases
  kb_locations
  kb_persons
)

printf "%-35s %10s %10s\n" "TABLE" "AWS" "NEON"
printf "%-35s %10s %10s\n" "-----" "---" "----"

for table in "${TABLES[@]}"; do
  aws_count=$(psql "$AWS_DB_URL" -t -A -c "SELECT COUNT(*) FROM $table;" 2>/dev/null || echo "N/A")
  neon_count=$(psql "$NEON_DB_URL_DIRECT" -t -A -c "SELECT COUNT(*) FROM $table;" 2>/dev/null || echo "N/A")
  printf "%-35s %10s %10s\n" "$table" "$aws_count" "$neon_count"
done
