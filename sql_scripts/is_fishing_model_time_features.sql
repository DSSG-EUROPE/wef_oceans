-- training_data year, month, and day of week feature generation
ALTER TABLE ais_is_fishing_model.training_data_features ADD year int8;
UPDATE ais_is_fishing_model.training_data_features SET year = date_part('year', utc_timestamp);
ALTER TABLE ais_is_fishing_model.training_data_features ADD month int8;
UPDATE ais_is_fishing_model.training_data_features SET month = date_part('month', utc_timestamp);
ALTER TABLE ais_is_fishing_model.training_data_features ADD day_of_week int8;
UPDATE ais_is_fishing_model.training_data_features SET day_of_week = date_part('dow', utc_timestamp);


-- test data SPIRE year, month, and day of week feature generation
ALTER TABLE ais_is_fishing_model.test_data_features ADD year int8;
UPDATE ais_is_fishing_model.test_data_features SET year = date_part('year', timestamp);
ALTER TABLE ais_is_fishing_model.test_data_features ADD month int8;
UPDATE ais_is_fishing_model.test_data_features SET month = date_part('month', timestamp);
ALTER TABLE ais_is_fishing_model.test_data_features ADD day_of_week int8;
UPDATE ais_is_fishing_model.test_data_features SET day_of_week = date_part('dow', timestamp);

-- change lon, lat to longitude and latitude so train and test have same feature names
ALTER TABLE ais_is_fishing_model.training_data_features RENAME COLUMN lat TO latitude ;
ALTER TABLE ais_is_fishing_model.training_data_features RENAME COLUMN lon TO longitude ;_
