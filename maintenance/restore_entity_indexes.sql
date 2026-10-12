-- Run with psql on the dev writer, outside a transaction.
-- Creates missing equivalent indexes; does not drop existing indexes.
\set ON_ERROR_STOP on
\set AUTOCOMMIT on

SET statement_timeout = 0;
SET lock_timeout = '5s';

WITH desired(index_name, method, columns, is_unique) AS (
    VALUES
        ('idx_entity_entity', 'btree', ARRAY['entity'], false),
        ('idx_entity_geometry', 'gist', ARRAY['geometry'], false),
        ('idx_entity_point', 'gist', ARRAY['point'], false),
        ('idx_entity_name', 'btree', ARRAY['name'], false),
        ('idx_entity_entry_date', 'btree', ARRAY['entry_date'], false),
        ('idx_entity_start_date', 'btree', ARRAY['start_date'], false),
        ('idx_entity_end_date', 'btree', ARRAY['end_date'], false),
        ('idx_entity_dataset', 'btree', ARRAY['dataset'], false),
        ('idx_entity_organisation_entity', 'btree', ARRAY['organisation_entity'], false),
        ('idx_entity_prefix', 'btree', ARRAY['prefix'], false),
        ('idx_entity_reference', 'btree', ARRAY['reference'], false),
        ('idx_entity_typology', 'btree', ARRAY['typology'], false)
), existing AS (
    SELECT i.indisvalid, i.indisready, i.indisunique, am.amname,
           i.indpred, i.indexprs,
           ARRAY(
               SELECT a.attname::text
               FROM unnest(i.indkey::smallint[]) WITH ORDINALITY AS k(attnum, position)
               JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = k.attnum
               ORDER BY k.position
           ) AS columns
    FROM pg_index i
    JOIN pg_class c ON c.oid = i.indexrelid
    JOIN pg_am am ON am.oid = c.relam
    WHERE i.indrelid = 'public.entity'::regclass
)
SELECT format(
    'CREATE %sINDEX CONCURRENTLY %I ON public.entity USING %I (%s);',
    CASE WHEN d.is_unique THEN 'UNIQUE ' ELSE '' END,
    d.index_name, d.method,
    (SELECT string_agg(format('%I', col), ', ') FROM unnest(d.columns) AS col)
)
FROM desired d
WHERE NOT EXISTS (
    SELECT 1 FROM existing e
    WHERE e.indisvalid AND e.indisready
      AND e.indpred IS NULL AND e.indexprs IS NULL
      AND e.amname = d.method AND e.columns = d.columns
      AND (NOT d.is_unique OR e.indisunique)
)
ORDER BY CASE d.index_name
    WHEN 'idx_entity_entity' THEN 0
    WHEN 'idx_entity_geometry' THEN 1
    WHEN 'idx_entity_point' THEN 2
    ELSE 3
END, d.index_name
\gexec

ANALYZE public.entity;

RESET statement_timeout;
RESET lock_timeout;

SELECT c.relname AS index_name, i.indisvalid AS valid,
       i.indisready AS ready, i.indisprimary AS primary_key,
       pg_get_indexdef(i.indexrelid) AS definition
FROM pg_index i
JOIN pg_class c ON c.oid = i.indexrelid
WHERE i.indrelid = 'public.entity'::regclass
ORDER BY c.relname;

-- The legacy wide composite index is deliberately excluded: migration
-- 543a95beb74b removes it. It is not needed to restore the individual indexes.
-- The entity lookup index deliberately permits duplicates: dev contains duplicate
-- entity IDs. Restoring uniqueness/primary-key constraints requires a separate
-- data investigation; this script does not remove or modify entity rows.
