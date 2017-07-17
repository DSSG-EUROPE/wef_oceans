# Oceans Data Challenge

Every year around 26 million tonnes of seafood worth close to $24 billion are extracted from the planet's oceans by illegal, unreported and unregulated (IUU) fishing. These IUU fishing techniques include: extracting fish from waters of other nations or designated marine protected areas, catching fish using illegal and ecologically damaging techniques, or under-declaring fish by transshipment at sea. Such practices are especially rife in the rich tropical waters of Southeast Asia due to the burgeoning demand in the region, and challenges of enforcement. This project sets out to address the problem of IUU fishing by correlating multiple data sources, and using data science techniques to identify vessels involved in IUU fishing.

Overfishing and IUU fishing have lead to huge declines in fish stock and some species such as tuna have declined by over 90%. Our project partner the World Economic Forum (WEF) is committed to improving the state of the world by engaging business, political, academic, and other leaders of society to shape global, regional, and industry agendas. In particular the WEF promotes initiatives to improve ocean governance, food chain sustainability, and environmental conservation.

In partnership with the WEF this DSSG Europe project has set out to create an open-source tool combining multiple data sources to help combat IUU fishing. This proof-of-principle study of fishing in the Torres Strait aimed to demonstrate how data aggregation from sources such as satellite imagery, synthetic aperture radar (SAR) and automatic identification systems (AIS) can be correlated and used with data science methods such as object recognition and anomaly detection to aid in identification of illegal fishing. This data science approach to detecting IUU fishing could ultimately improve enforcement, guide governance, and inform policy decision making.

There are many challenges associated with detecting IUU fishing. Firstly, the world's ocean comprise the majority of the Earth’s surface (71%). This is a large area to inspect and hence the volumes of data involved are large. There are many vessels in this large area relating to commercial, leisure, or fishing activities. Systems to detect and track these vessels such as automatic identification systems (AIS) tend to be implemented nationally in vessel management systems (VMS), hence there is little standardization of the data format. Satellite data on the other hand is relatively infrequent, can be obscured by cloud cover, and may not have good coverage in the ocean. Combining these data sources can be difficult to find appropriate images and AIS data. There is also a distinct lack of high-resolution open-source data sources in this domain, due to the cost of data collection. 

A socially desirable outcome for this project would be to successfully demonstrate how these data can be used to identify IUU fishing. In partnership with the WEF and organisations this can be conveyed to policy and decision makers to expand the study. A socially desirable outcome would be to improve detection of illegal fishing via these data sources, a secondary outcome of this would be to provide improved enforcement of illegal fishing, which in turn would improve regulation as it becomes harder to evade capture. The result of this would be to promote more sustainable fishing practice and environmental conservation. 

```
.
├── data
│   └── ais_query.py
├── docs
│   ├── database.ini
│   └── iuu_list_of_lists.csv
├── envs
│   ├── ais_env.yml
│   ├── gbdx_env.yml
│   └── modis_env.yml
├── LICENSE
├── models
├── notebooks
│   ├── data_exploration
│   │   ├── 0.0-wg-ais_eda_2month.ipynb
│   │   ├── 0.1-wg-ais_eda_1year.ipynb
│   │   ├── 1.0-wg-ais_iuu_list_intersection_2month.ipynb
│   │   ├── 1.1-wg-ais_iuu_list_intersection_1year.ipynb
│   │   └── 2.0-im-ais_gbdx_intersection.ipynb
│   ├── gbdx
│   │   ├── gbdx_data_description_html.ipynb
│   │   └── gbdx_data_description.ipynb
│   └── planet
│       ├── planet_labs_data_ais.ipynb
│       └── planet_search.py
├── __pycache__
│   └── ais_query.cpython-35.pyc
├── README.md
├── reports
│   └── gbdx_torres_strait_coverage.html
└── src
    ├── feature_generation
    │   └── distance_from_shore.ipynb
    ├── __init__.py
    └── models
        └── Fishing or not model.ipynb
```

## Automatic Identification System (AIS) data
Data for this project was provided by SPIRE
https://spire.com/

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
