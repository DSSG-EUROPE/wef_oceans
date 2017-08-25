# Developing a Fishing Risk Framework from Satellites and Ocean Data
This project as part of Data Science for Social Good (DSSG) Europe 2017 combines multiple data sources to generate a fishing vessel risk score. The desired use of this risk score is to provide governmenrts, NGOs, retailers, and enforcement agencies the information required to identify vessels fishing in an illegal, unregulated or unreported way.

This work was conducted in partnership with the World Economic Forum as part of the 'New Vision for the Oceans'. 

This repository contains to process Automatic Identification System (AIS) data, and satellite imagery.

## Data providers

Data for this project was provided by SPIRE
https://spire.com/

## Installation
## Usage

## Authors

## Acknowledgments

## License
This project is licensed under the MIT License - see the LICENSE.md file for details


<!--

### Uploading data to database from S3 to AWS (wef-oceans)

1. explore data in the bucket (check permissions in ~/.aws/credentials)
`aws s3 --profile dssg2017 ls s3://dssg2017-wef --recursive`
[can use the --human-readable --summarize flags]

2. eownload the data (remember to change cd to /mnt/data/shared)
`aws s3 --profile dssg2017 cp s3://dssg2017-wef . --recursive`
[The command will create a new folder and will not copy the files that already exist]

3. explore and concatenate files (both static and positional)
```
files=(*static*)
{ head -n1 ${files[0]}; for f in ${files[*]}; do tail -n+2 "$f"; done; } > static_concat.csv

files=(*static*)
{ head -n1 ${files[0]}; for f in ${files[*]}; do tail -n+2 "$f"; done; } > position_concat.csv
```

4. create DB schema
`CREATE SCHEMA ais_messages;`

5. generate sql table with csvsql for static ais data
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

6. generate sql table with csvsql for position ais data
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


7. upload data to database by psql
`cat static_concat.csv | psql -c "\copy ais_messages.full_year_static from stdin with csv header;"`
similarly for positional data
`cat position_concat.csv | psql -c "\copy ais_messages.full_year_position from stdin with csv header;"`

8. create geom column for positional coordinates
```
ALTER TABLE ais_messages.full_year_position ADD COLUMN geom geometry(Point,4326);
UPDATE ais_messages.full_year_position SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326);
```

9. index database
```
CREATE INDEX full_year_position_mmsi_idx ON ais_messages.full_year_position (mmsi) ;
CREATE INDEX full_year_position_geom_idx ON ais_messages.full_year_position (geom) ;
CREATE INDEX full_year_static_mmsi_idx ON ais_messages.full_year_static (mmsi) ;
```

10. clean data

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
