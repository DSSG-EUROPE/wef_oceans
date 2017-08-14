from src.sat_imagery import gbdx_intersection as sat
import utils
from utils import db_connect
import pandas as pd

###############################################################
###################### OPEN POSTGRESQL CONN ###################
###############################################################

engine_output = db_connect.alchemy_connect()
conn_output = engine_output.connect()

###############################################################
################ CREATE SOME NEW VARIABLES  ###################
###############################################################

ais_gbdx_overlap = pd.read_sql_query("SELECT * FROM gbdx_metadata.overlap_marine_ocean_areas",con=engine_output)
ais_gbdx_overlap["time_diff"] = (abs(ais_gbdx_overlap.timestamp - ais_gbdx_overlap.timestamps)).astype('timedelta64[s]')

###############################################################
#################### CREATE POINT BUFFERS  ####################
###############################################################

points_buffers = [sat.create_buffers_points(x) for x in ais_gbdx_overlap['geom']]
imgs = list(ais_gbdx_overlap['catalogID'])

###############################################################
################### START GBDX WORKORDERS #####################
###############################################################

order_id_list = [sat.processing_gbdx(x, y) for x, y in zip(imgs, points_buffers)]

with open("results_test.txt", "w") as file:
        for item in order_id_list:
            file.write("%s\n" %item.id)
        file.close()

