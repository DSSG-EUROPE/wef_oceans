--Create marine protected areas table (Ia are the most stringent ones)
CREATE TABLE world_protected_areas.marine_areas AS
SELECT *
FROM world_protected_areas.protected_areas
WHERE MARINE IN ('1', '2') AND IUCN_CAT='Ia';

--Create index on geom column
CREATE INDEX marine_areas_gix ON world_protected_areas.marine_areas USING GIST (geom); 

--Change geom name on protected areas to avoid name conflicts
ALTER TABLE world_protected_areas.marine_areas RENAME COLUMN geom to marine_geom;
ALTER TABLE world_protected_areas.marine_areas RENAME COLUMN status to status_pa;

--Create new table with intersection between points and polygons inside the same schema
CREATE TABLE world_protected_areas.ais_protected_areas AS
SELECT * 
FROM ais_messages.full_year_position pts
INNER JOIN world_protected_areas.marine_areas pol
ON ST_Within(pts.geom, pol.marine_geom);
