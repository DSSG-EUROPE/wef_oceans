/*
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
*/

-- add a mean is fishing score
ALTER TABLE unique_vessel.aggregated_register_components ADD COLUMN IF NOT EXISTS mean_is_fishing float8;
WITH t AS (
	-- Any generic query which returns rowid and corresponding calculated values
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

--ALTER TABLE unique_vessel.aggregated_register_components DROP COLUMN mean_is_fishing;
