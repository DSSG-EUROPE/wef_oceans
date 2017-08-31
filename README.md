# A Fishing Risk Framework from Satellites and Ocean Data
This proof-of-concept system creates a fishing vessel risk framework to assess the likelihood of a vessel engaging in illegal, unregulated, or unreported (IUU) fishing. The framework uses multiple indicators to evaluate a vessel and suggest whether it is likely to be involved in IUU fishing, with the information being displayed in a front end web application.

Several indicators have been included in this working proof-of-concept, including the likelihood that a vessel has previously been fishing in a marine protected area (MPA) or exclusive economic zone (EEZ), and the intermittency of the AIS signal. These indicators can be weighted according to the use case or for convenience combined into a unified vessel risk score.

A unique aspect of the proposed fishing risk framework comes from the ability to combine AIS data with satellite imagery building a library of data from multiple sources about each vessel.

## Requirements
This pipeline requires a PostgreSQL database, Anaconda Python version 3, and R version 3. Preprocessing, feature generation, and modelling was performed in Python, with risk indicators created in PSQL, and the web application made in Rshiny. 

- Define locations for repository, data, models, and add root folder to  python path `conda env create -f environment.yml`
- Create conda environment for pipeline `conda env create -f envs/development.yml`

## How to run the pipeline




## Collaborations
* World Economic Forum (https://www.weforum.org/)
* IBM (https://www.ibm.com/)


## Data providers
* Digital Globe, Inc. (http://www.digitalglobe.com/)
* Planet Labs, Inc. (https://www.planet.com/)
* Spire Global, Inc. (https://spire.com/)

## Authors
This project was conducted as part of Data Science for Social Good (DSSG) Europe 2017 fellowship, further details of the 12 week summer fellowship can be found here:
https://dssg.uchicago.edu/europe/

Data science fellows:
* Iván Higuera Mendieta
* Shubham Tomar
* William Grimes

Technical mentor:
* Jane Zanzig

Project manager:
* Paul van der Boor

## Acknowledgments
The authors would like to thank Euro Beinat and Nishan Degnarain for having the vision to persue a data science project for detection of IUU fishing vessels. Further the weekly calls and guidance with Nishan Degnarain and Steven Adler were instrumental to this projects success.

We also extend our thanks for the helpful input, and discussion with the following: Dan Hammer, Gregory Stone, Kristina Boerder, Kyle Brazil, Nathan Miller, and Paul Woods.

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
