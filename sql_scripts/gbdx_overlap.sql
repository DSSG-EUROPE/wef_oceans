
--Modify variables to overlap: geom and time without microseconds
ALTER TABLE gbdx_metadata.sat_imagery_meta
SELECT UpdateGeometrySRID('gbdx_metadata', 'sat_imagery_meta', 'footprintwkt', 4326);
UPDATE gbdx_metadata.sat_imagery_meta SET "timestamp" = date_trunc('second', "timestamp");

--Rename timestamp variable to avoid conflicts when joining databases
ALTER TABLE gbdx_metadta.sat_imagery_meta RENAME "timestamp" TO timestamps ;

--Create index: gist geom index
CREATE INDEX gbdx_metadta.sat_imagery_meta_gix ON gbdx_metadta.sat_imagery_meta  USING GIST(footprintwkt);

--Create new table
CREATE TABLE gbdx_metadata.overlap_marine_ocean_areas AS
SELECT *
FROM ais_messages.full_year_position pts
INNER JOIN gbdx_metadata.sat_imagery_meta  pol
ON (ST_Intersects(pts.geom, pol."footprintwkt")) and (@EXTRACT(EPOCH from age(pol.timestamps, pts."timestamp")) < 120);

