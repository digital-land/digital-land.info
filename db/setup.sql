CREATE EXTENSION postgis;

CREATE TABLE entity (
        entity bigint PRIMARY KEY,
        name TEXT,
        entry_date date,
        start_date date,
        end_date date,
        dataset TEXT,
        json JSONB,
        organisation_entity bigint,
        prefix TEXT,
        reference TEXT,
        typology TEXT,
        geojson JSONB,
        geometry geometry,
        point geometry
);

CREATE INDEX entity_index on entity (entity,name,entry_date,start_date,end_date,dataset,organisation_entity,prefix,reference,typology);
CREATE INDEX geometry_geom_idx ON entity USING GIST (geometry);
CREATE INDEX point_geom_idx ON entity USING GIST (point);

COPY entity(entity,name,entry_date,start_date,end_date,dataset,json,organisation_entity,prefix,reference,typology,geojson,geometry,point)
FROM :'filepath'
WITH (
    FORMAT CSV,
    HEADER,
    DELIMITER '|',
    FORCE_NULL(name,entry_date,start_date,end_date,dataset,organisation_entity,prefix,reference,typology,geojson,geometry,point)
);
