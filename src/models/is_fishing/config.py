features = dict(
    time_features = [
                     'year',
                     'month',
                     'day_of_week',
                     'sun_height',
                     'day_or_night'
                     ],
    movement_features = [
                         'speed',
                         'course'
                         ],
    location_features = [
                         'longitude',
                         'latitude',
                         'distance_to_shore',
#                         'shore_country',
                         'distance_to_port',
                         'in_eez'
                         ]
)


def get_features():
    time_features = config.features['time_features']
    location_features = config.features['location_features']
    movement_features = config.features['movement_features']
    all_features = time_features + location_features + movement_features
    return time_features, location_features, movement_features, all_features
