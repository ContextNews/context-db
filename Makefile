include .env
export

migrate-aws:
	DATABASE_URL='$(AWS_DB_URL)' poetry run alembic upgrade head

migrate-neon:
	DATABASE_URL='$(NEON_DB_URL_DIRECT)' poetry run alembic upgrade head

migrate-local:
	DATABASE_URL='$(AWS_DB_URL)' DB_SSLMODE=disable poetry run alembic upgrade head

shell-aws:
	psql '$(AWS_DB_URL)'

shell-neon:
	psql '$(NEON_DB_URL_DIRECT)'

copy-to-neon:
	bash scripts/copy_data_to_neon.sh

compare-counts:
	bash scripts/compare_row_counts.sh
