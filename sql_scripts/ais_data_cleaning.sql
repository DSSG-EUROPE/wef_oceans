DELETE
FROM ais_messages.full_year_position
WHERE (mmsi IS NULL OR mmsi < 100000000) 
OR (timestamp IS NULL OR timestamp = '1970-01-01 00:00:00') 
OR (longitude IS NULL OR longitude NOT BETWEEN -180 AND 180)
OR (latitude IS NULL OR latitude NOT BETWEEN -90 AND 90);

DELETE
FROM ais_messages.full_year_static
WHERE (mmsi IS NULL OR mmsi < 100000000) 
OR (timestamp IS NULL OR timestamp = '1970-01-01 00:00:00');
