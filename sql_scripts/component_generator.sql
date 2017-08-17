-- copy aggregated_register table to new table with componenets
CREATE TABLE unique_vessel.aggregated_register_components AS
SELECT table_1.mmsi, table_1.count_ais_position_yr, table_2.last_timestamp, table_2.last_longitude, table_2.last_latitude
FROM (SELECT * FROM unique_vessel.aggregated_register_position) AS table_1
INNER JOIN (SELECT DISTINCT ON (mmsi)
	    mmsi,
	    timestamp as last_timestamp,
	    longitude as last_longitude,
	    latitude as last_latitude 
	    FROM ais_is_fishing_model.test_data_predictions
	    ORDER BY mmsi, last_timestamp DESC) table_2
on (table_1.mmsi = table_2.mmsi);

-- component mean is fishing score
ALTER TABLE unique_vessel.aggregated_register_components ADD COLUMN IF NOT EXISTS mean_is_fishing float8;
WITH t AS (
	SELECT *
	FROM unique_vessel.aggregated_register_components AS t1
	INNER JOIN (SELECT mmsi as rowid, AVG(is_fishing) AS is_fishing_mean
		    FROM ais_is_fishing_model.test_data_predictions
	            GROUP BY mmsi) AS t2
	ON (t1.mmsi = t2.rowid)
)
UPDATE unique_vessel.aggregated_register_components
SET mean_is_fishing = t.is_fishing_mean
FROM t
WHERE unique_vessel.aggregated_register_components.mmsi = t.rowid;

-- component max is fishing score
ALTER TABLE unique_vessel.aggregated_register_components ADD COLUMN IF NOT EXISTS max_is_fishing float8;
WITH t AS (
	SELECT *
	FROM unique_vessel.aggregated_register_components AS t1
	INNER JOIN (SELECT mmsi as rowid, MAX(is_fishing) AS is_fishing_max
		    FROM ais_is_fishing_model.test_data_predictions
	            GROUP BY mmsi) AS t2
	ON (t1.mmsi = t2.rowid)
)
UPDATE unique_vessel.aggregated_register_components
SET max_is_fishing = t.is_fishing_max
FROM t
WHERE unique_vessel.aggregated_register_components.mmsi = t.rowid;

-- component mpa_count
ALTER TABLE unique_vessel.aggregated_register_components ADD COLUMN IF NOT EXISTS mpa_count int8;
WITH t AS (
	SELECT t1.mmsi, COALESCE(t2.mpa_count, 0) AS mpa_count
	FROM unique_vessel.aggregated_register_components AS t1
	LEFT JOIN (SELECT mmsi as rowid, mpa_count
		   FROM world_protected_areas.ais_mpa_grouped) AS t2
	ON (t1.mmsi = t2.rowid)
)
UPDATE unique_vessel.aggregated_register_components
SET mpa_count = t.mpa_count
FROM t
WHERE unique_vessel.aggregated_register_components.mmsi = t.mmsi;

-- component mpa_count normalised
ALTER TABLE unique_vessel.aggregated_register_components ADD COLUMN IF NOT EXISTS mpa_count_norm float8;
WITH t AS (
    SELECT t1.mmsi, t1.mpa_count::float / t1.count_ais_position_yr::float AS mpa_count_norm
    FROM unique_vessel.aggregated_register_components AS t1
)
UPDATE unique_vessel.aggregated_register_components
SET mpa_count_norm = t.mpa_count_norm
FROM t
WHERE unique_vessel.aggregated_register_components.mmsi = t.mmsi;

-- component mpa_time_seconds
ALTER TABLE unique_vessel.aggregated_register_components ADD COLUMN IF NOT EXISTS mpa_time_seconds int8;
WITH t AS (
	SELECT t1.mmsi, COALESCE(t2.mpa_time_seconds, 0) AS mpa_time_seconds
	FROM unique_vessel.aggregated_register_components AS t1
	LEFT JOIN (SELECT mmsi as rowid, mpa_time_seconds
		   FROM world_protected_areas.ais_mpa_grouped) AS t2
	ON (t1.mmsi = t2.rowid)
)
UPDATE unique_vessel.aggregated_register_components
SET mpa_time_seconds = t.mpa_time_seconds
FROM t
WHERE unique_vessel.aggregated_register_components.mmsi = t.mmsi;

-- component eez_count
ALTER TABLE unique_vessel.aggregated_register_components ADD COLUMN IF NOT EXISTS eez_count integer;
WITH t AS (
	SELECT *
	FROM unique_vessel.aggregated_register_components AS t1
	INNER JOIN (SELECT mmsi as rowid, SUM(in_eez) AS count_eez
		    FROM ais_is_fishing_model.test_data_predictions
	            GROUP BY mmsi) AS t2
	ON (t1.mmsi = t2.rowid)
)
UPDATE unique_vessel.aggregated_register_components
SET eez_count = t.count_eez
FROM t
WHERE unique_vessel.aggregated_register_components.mmsi = t.rowid;

-- component mpa_count normalised
ALTER TABLE unique_vessel.aggregated_register_components ADD COLUMN IF NOT EXISTS eez_count_norm float8;
WITH t AS (
    SELECT t1.mmsi, t1.eez_count::float / t1.count_ais_position_yr::float AS eez_count_norm
    FROM unique_vessel.aggregated_register_components AS t1
)
UPDATE unique_vessel.aggregated_register_components
SET eez_count_norm = t.eez_count_norm
FROM t
WHERE unique_vessel.aggregated_register_components.mmsi = t.mmsi;

-- component vessel_country added from mmsi mid
ALTER TABLE unique_vessel.aggregated_register_components ADD COLUMN IF NOT EXISTS vessel_country varchar(50);
WITH t AS (
    SELECT t1.mmsi, SUBSTRING(t1.mmsi::text, 1, 3)::int4 AS mid, t2.rowid, t2.country
    FROM unique_vessel.aggregated_register_components AS t1
    LEFT JOIN (SELECT mid::int4 AS rowid, country FROM ais_messages.ais_mmsi_mid) AS t2
    ON SUBSTRING(t1.mmsi::text, 1, 3)::int4 = t2.rowid
)
UPDATE unique_vessel.aggregated_register_components
SET vessel_country = t.country
FROM t
WHERE unique_vessel.aggregated_register_components.mmsi = t.mmsi;
