from utils import db_connect
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(color_codes=True)


df = db_connect.query("SELECT mmsi, is_fishing, distance_to_shore \
                        FROM ais_is_fishing_model.test_data_predictions \
                        where is_fishing >= 0.7;")

df_static_fishing_reported = db_connect.query("select * from ais_messages.full_year_static \
                                              where ship_and_cargo_type = 30")


sns.distplot(df['distance_to_shore'], bins=1000)
plt.show()


reported_fishing = df[df['mmsi'].isin(df_static_fishing_reported['mmsi'])]
reported_fishing_mmsi = reported_fishing.groupby(['mmsi'])['is_fishing'].mean()


df_static_fishing_unreported = db_connect.query("select * from ais_messages.full_year_static \
                                                where ship_and_cargo_type != 30")

unreported_fishing = df[df['mmsi'].isin(df_static_fishing_unreported['mmsi'])]
unreported_fishing_mmsi = unreported_fishing.groupby(['mmsi'])['is_fishing'].mean()


sns.distplot(reported_fishing.is_fishing, label='Reported Fishing')
sns.distplot(unreported_fishing.is_fishing, color='r', label='Unreported Fishing')


plt.show()
