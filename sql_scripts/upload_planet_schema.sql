---    Create schema  ----
CREATE SCHEMA planet_metadata;

--Create schema for Planet metadata
CREATE TABLE planet_metadata.planet_metadata_south_china (
	acquired VARCHAR(27) NOT NULL, 
	anomalous_pixels FLOAT NOT NULL, 
	black_fill FLOAT, 
	catalog_id FLOAT, 
	cloud_cover FLOAT NOT NULL, 
	columns INTEGER NOT NULL, 
	epsg_code INTEGER NOT NULL, 
	grid_cell FLOAT, 
	ground_control FLOAT NOT NULL, 
	gsd FLOAT NOT NULL, 
	instrument VARCHAR(4), 
	item_type VARCHAR(12) NOT NULL, 
	origin_x INTEGER NOT NULL, 
	origin_y INTEGER NOT NULL, 
	pixel_resolution INTEGER NOT NULL, 
	provider VARCHAR(11) NOT NULL, 
	published VARCHAR(20) NOT NULL, 
	quality_category VARCHAR(8), 
	rows INTEGER NOT NULL, 
	satellite_id VARCHAR(10) NOT NULL, 
	strip_id INTEGER NOT NULL, 
	sun_azimuth FLOAT NOT NULL, 
	sun_elevation FLOAT NOT NULL, 
	updated VARCHAR(20) NOT NULL, 
	usable_data FLOAT NOT NULL, 
	view_angle FLOAT NOT NULL, 
	id VARCHAR(34) NOT NULL, 
	geom_wkt GEOMETRY(POLYGON) NOT NULL, 
	geom_type VARCHAR(7) NOT NULL
	
);
