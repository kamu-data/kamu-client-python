import json


def df_to_geojson(df, geom="geometry"):
    """
    Converts Pandas data frame to GeoJson-like object
    """
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": json.loads(record.pop(geom)),
                "properties": record,
            }
            for record in json.loads(df.to_json(orient="records"))
        ],
    }
