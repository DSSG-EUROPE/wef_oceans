# An Illegal Fishing Vessel Risk Framework - Satellite imagery

### Requirements and authentications
Our satellite images providers are commercial. In order to run the codes inside this repository you must have an active account for [Digital Globe] or [Planet Labs]. Each provider has its own API to query, activate, preprocess, and download imagery. Both API's are listed in the `development` environment and can be installed excecuting the following: 

```bash
source environment_variables
conda env create -f envs/development.yml
source activate development
```

Digital Globe API, [GBDX], is Python native and needs the user to define authentication credentials under `~/.gbdx_config` (see API documentation). To run [Planet API] the user needs to define a environment variable with the API key named `PLANET_API_KEY`. In this repo, the key is defined in: `./auth/db_credentials_example` 

In order to upload data to our PostgreSQL database and use its geometry operations, we need to create the schemas to upload the data. To do this, we need to run first the following:

```bash
psql -f ./sql_scripts/upload_gbdx_schema.sql
psql -f ./sql_scrips/upload_planet_schema.sql
```

### Running the code

As described in the Technical documentation, a supplementary part of the analysis includes the visual validation of vessel position data. This is done for our two sources of imagery following a common fashion. First, we retrieve imagery metadata from marine areas in the whole world using each provider API in our defined timeframe (May 2016 - Jun 2017). Second, we find the spatial and temporal overlap of the vessel positional data with the images using PostgreSQL and PostGIS and create a new SQL table. Third, we load the overlap subset and create for each vessel positional point a buffer and use it to crop the satellite image. 

#### 1. Retrieve imagery:

GBDX: `python src/sat_imagery/get_images_metadata.py`


Planet: `python src/sat_imagery/search-items.py` 

Digital Globe's code will iterate the query for each marine and ocean area in the world (see [CartoDB Boundaries]). Planet Labs code will look for an area defined in the `coords.json` file in the same directory, you can check the [Geojson geometry builder] to create a new area of interest. Both files will upload the metadata table directly to defined SQL Schemas. Additionally, the Planet `search-items.py` will save a HTML Leaflet map to explore the retrieved data. 

#### 2. Intersection: 

GBDX: `psql -f ./sql_scripts/overlap_gbdx.sql`


Planet: `psql -f ./sql_scrips/overlap_planet.sql`

Both codes will create a SQL query which will create a new table with the total of vessel positional points inside the polygon of the images. 

#### 3. Croping and dowloading
GBDX: `python src/sat_imagery/retrieve_gbdx_crop.py`

Planet: `python src/sat_imagery/planet_check.py `

The GBDX code will create the buffers and use the GBDX's API crop task to retrieve the cropped images. This images are downloaded to the client S3 bucket. For Planet, the code will project and crop the downloaded images using the `rasterio` library. The code also will save a mosaic of selected cropped images 

[Digital Globe]:http://www.digitalglobe.com/
[Planet Labs]:https://www.planet.com/
[GBDX]:http://gbdxtools.readthedocs.io/en/latest/
[Planet API]:https://planetlabs.github.io/planet-client-python/index.html
[CartoDB Boundaries]: https://cartodb.github.io/bigmetadata/global/boundary.html
[Geojson geometry builder]:http://geojson.io/#map=2/20.0/0.0
