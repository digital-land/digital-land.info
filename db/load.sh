export PGPASSWORD=postgres
psql -h localhost -p 5432 -U postgres digital_land -v filepath='/exported_entities.tsv' -f setup.sql
