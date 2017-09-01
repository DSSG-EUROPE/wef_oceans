
--Modify variables to overlap: geom and time without microseconds
ALTER TABLE planet_metadata.planet_metadata_south_china 
ALTER COLUMN geom_wkt TYPE GEOMETRY(POLYGON,0);
SELECT UpdateGeometrySRID('planet_metadata', 'planet_metadata_south_china', 'geom_wkt', 4326);
UPDATE planet_metadata.planet_metadata_south_china SET acquired = date_trunc('second', acquired);
--Create index: gist geom index
CREATE INDEX planet_metadata_china_gix ON planet_metadata.planet_metadata_south_china USING GIST(geom_wkt);
--Create new table
CREATE TABLE planet_metadata.overlap_south_china_planet AS
SELECT *
FROM ais_messages.full_year_position pts
INNER JOIN planet_metadata.planet_metadata_south_china pol
ON (ST_Intersects(pts.geom, pol.geom_wkt)) and (@EXTRACT(EPOCH from age(pol.acquired, pts."timestamp")) < 120);


