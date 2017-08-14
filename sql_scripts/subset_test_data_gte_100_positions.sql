CREATE TABLE ais_is_fishing_model.test_data_features_gte_100_positions AS 
SELECT *
FROM ais_is_fishing_model.test_data_features
WHERE mmsi IN (SELECT mmsi FROM unique_vessel.aggregated_register WHERE count_ais_position_yr > 100);
