# An Illegal Fishing Vessel Risk Framework
This proof-of-concept system creates a vessel risk framework to assess the likelihood that a vessel engaging in illegal,
unregulated, or unreported (IUU) fishing at a given point in time. The framework combines automatic identification system (AIS)
 tracking data with satellite imagery to show how multiple data sources can be combined to build a library of historic evidence 
and data reflecting a vessel's behaviour. Thus far several indicators have been included, including the likelihood 
that a vessel has previously fished in a marine protected area (MPA) or exclusive economic zone (EEZ), and the 
intermittency of the vessel's AIS signal. 

Vessel risk indicators can be considered individually, weighted according to the use case, or combined into a unified 
vessel risk score. This information is displayed in a front end web application. This application gives governments, 
NGOs, retailers, and enforcement agencies the information to distinguish responsible, legitimate vessels from 
vessels doing IUU fishing. For example, this could be used by retailers to check the risk score of vessels that supply
their tuna, or to guide enforcement agencies in choosing which areas to patrol. 

## How to run the pipeline
Running this pipeline requires a PostgreSQL database, Anaconda Python 3.4, and R (3.4.1). Pre-processing, 
feature generation, and modelling were performed in Python, with risk indicators created in PSQL, and the web application 
made in R Shiny. A separate pipeline to run the intersection between AIS tracking data and satellite imagery can be 
consulted [here](../master/src/sat_imagery/README.md). Instructions to run the RShiny app are 
[here](../master/shiny_app/README.md)

### Requirements
Before running the pipeline the following commands should be executed:
* Create database credential files: `auth/db_credentials` (see `auth/db_credentials_example`), `/auth/database_alchemy.ini` (see `auth/database_alchemy.dummy`) and `/auth/database_psycopg2.ini` (see `auth/database_psycopg2.dummy`)
* Define environmental variables: `source environment_variables`
* Create conda environment for pipeline: `conda env create -f envs/development.yml`

### 1. Download shape files for distance feature generation
This will download shape files of coastlines and locations of ports, to be used for vessel distance calculations 
in the preprocessing and feature generation steps.

`python src/features/ais_distance_calculations.py`

### 2. Data cleaning
This PostgreSQL command removes nulls, unix timestamps, and coordinates beyond the range for positional and 
then static data:

`psql -f ./sql_scripts/ais_data_cleaning.sql`

### 3. Create schema for modelling
`psql -c 'CREATE SCHEMA IF NOT EXISTS ais_is_fishing_model;'`

### 4. Pre-processing and feature generation 
This script removes duplicate data and null values and generates additional features, including distance to shore
and distance to port for each vessel at each time point, and whether it is nighttime or daytime. 

`python src/models/is_fishing/preprocess_data.py`

### 5. Train model to predict whether a vessel is fishing at each time point
This uses labelled training data to generate a model to predict whether a vessel is fishing at each time point. 
A random forest model with 450 trees was used and the model output was saved in the `models` directory.

`python src/models/is_fishing/train_is_fishing.py`

### 6. Predict if vessel is fishing
This code reads from the PostgreSQl database in chunks and predicts for each vessel at each time point the 
probability that it is fishing.

`python src/models/is_fishing/predict_is_fishing.py`

### 7. Create vessel aggregate features
This creates a count of the number of available rows in both AIS static and positional data for each MMSI.

`psql -f ./sql_scripts/create_unique_vessel_register.sql`

### 8. Create a score of the number of times vessel was in marine protected areas over a given time period
First, running `bash ./sql_scripts/get_wdpa.sh` will download a shapefile with all the 
[World Protected Areas](https://www.protectedplanet.net), and create and upload the schema and the data to a 
PostgreSQL instance. Second, using the uploaded table, the `marine_protected_areas_within.sql` script will 
create a unique vessel score to account for the presence of vessels in MPA's:

`psql -f ./sql_scripts/marine_protected_areas_within.sql`

### 9. Generate vessel risk indicators
Based on the existing tables, aggregate vessel MMSI indicators are created in this script:

`psql -f ./sql_scripts/component_generator.sql`

## Collaborations
* World Economic Forum (https://www.weforum.org/)
* IBM (https://www.ibm.com/)

## Data providers
* Digital Globe, Inc. (http://www.digitalglobe.com/)
* Planet Labs, Inc. (https://www.planet.com/)
* Spire Global, Inc. (https://spire.com/)

## Authors
This project was conducted as part of Data Science for Social Good (DSSG) Europe 2017 fellowship, further details of 
the twelve week summer fellowship can be found here:
https://dssg.uchicago.edu/europe/

**Data science fellows:** Iván Higuera Mendieta, Shubham Tomar, and William Grimes

**Technical mentor:** Jane Zanzig

**Project manager:** Paul van der Boor

## Acknowledgments
The authors would like to thank Euro Beinat and Nishan Degnarain for having the vision to pursue a data science project 
for detection of illegal, unreported, and unregulated fishing vessels. Further our weekly calls with Nishan Degnarain, and 
Steven Adler were instrumental in guiding this project to success.

We also extend our thanks to the following for their input, and helpful discussions: Dan Hammer, Gregory Stone, 
Kristina Boerder, Kyle Brazil, Nathan Miller, and Paul Woods.

## License
This project is licensed under the MIT License - see the LICENSE.md file for details

<!--

### Uploading data to database from S3 to AWS (wef-oceans)

1. Explore data in the bucket (check permissions in `~/.aws/credentials`)
`aws s3 --profile dssg2017 ls s3://dssg2017-wef --recursive`
[can use the `--human-readable --summarize` flags]

2. Download the data (remember to `cd /mnt/data/shared`)
`aws s3 --profile dssg2017 cp s3://dssg2017-wef . --recursive`
[The command will create a new folder and will not copy the files that already exist]

3. Explore and concatenate files (both static and positional)
```
files=(*static*)
{ head -n1 ${files[0]}; for f in ${files[*]}; do tail -n+2 "$f"; done; } > static_concat.csv

files=(*static*)
{ head -n1 ${files[0]}; for f in ${files[*]}; do tail -n+2 "$f"; done; } > position_concat.csv
```

4. Create DB schema:
`CREATE SCHEMA ais_messages;`

5. Generate SQL table with `csvsql` for static AIS data:
`head -n 3000000 static_concat.csv | iconv -t ascii | tr [:upper:] [:lower:] | tr ' ' '_' | csvsql -i postgresql`

```
CREATE TABLE ais_messages.full_year_static (
        msg_type INTEGER, 
        mmsi INTEGER, 
        timestamp TIMESTAMP, 
        imo FLOAT, 
        name VARCHAR(20), 
        ship_and_cargo_type FLOAT, 
        length FLOAT, 
        width FLOAT, 
        draught FLOAT, 
        eta_date VARCHAR(23), 
        call_sign VARCHAR(7), 
        destination VARCHAR(20)
);
```

6. Generate SQL table with `csvsql` for position ais data
`head -n 3000000 position_concat.csv | iconv -t ascii | tr [:upper:] [:lower:] | tr ' ' '_' | csvsql -i postgresql`

```
CREATE TABLE ais_messages.full_year_position (
        msg_type INTEGER, 
        mmsi INTEGER, 
        timestamp TIMESTAMP, 
        status INTEGER, 
        rot INTEGER, 
        speed FLOAT, 
        accuracy INTEGER, 
        longitude FLOAT, 
        latitude FLOAT, 
        course FLOAT, 
        heading INTEGER, 
        maneuver INTEGER
);
```


7. Upload data to database using `psql`:
`cat static_concat.csv | psql -c "\copy ais_messages.full_year_static from stdin with csv header;"`
Similarly for positional data:
`cat position_concat.csv | psql -c "\copy ais_messages.full_year_position from stdin with csv header;"`

8. Create geom column for positional coordinates:
```
ALTER TABLE ais_messages.full_year_position ADD COLUMN geom geometry(Point,4326);
UPDATE ais_messages.full_year_position SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326);
```

9. Index database:
```
CREATE INDEX full_year_position_mmsi_idx ON ais_messages.full_year_position (mmsi) ;
CREATE INDEX full_year_position_geom_idx ON ais_messages.full_year_position (geom) ;
CREATE INDEX full_year_static_mmsi_idx ON ais_messages.full_year_static (mmsi) ;
```

10. Clean data:

```
DELETE
FROM ais_messages.full_year_position
WHERE (mmsi IS NULL OR mmsi < 100000000) 
OR (timestamp IS NULL OR timestamp = '1970-01-01 00:00:00') 
OR (longitude IS NULL OR longitude NOT BETWEEN -180 AND 180)
OR (latitude IS NULL OR latitude NOT BETWEEN -90 AND 90);

```

```
DELETE
FROM ais_messages.full_year_static
WHERE (mmsi IS NULL OR mmsi < 100000000) 
OR (timestamp IS NULL OR timestamp = '1970-01-01 00:00:00');
```
-->
