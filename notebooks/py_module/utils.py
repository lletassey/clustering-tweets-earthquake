import datetime
import pandas as pd
import geopandas as gpd
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon


def create_hulls(tweets, clustering_algo, coords):
    # Create a hulls geodataframe
    hulls = gpd.GeoDataFrame(
        columns=["num_tweets", "area_km2", "start_time_ts", "geometry"]
    )

    # Iterate over unique clusters (excluding noise)
    for cluster in set(clustering_algo.labels) - {-1}:
        # Get the coordinates of the points in cluster
        points = coords[clustering_algo.labels == cluster]
        # Create a convex hull (try/except to handle fallible cases)
        try:
            hull = ConvexHull(points)
        except:
            continue
        # Add founding time of cluster
        start_time = tweets[tweets.index.get_level_values(0) == cluster][
            "createdAt"
        ].min()
        start_time = datetime.datetime.fromtimestamp(start_time.timestamp()).replace(
            microsecond=0
        )
        # Append the cluster and hull to the geodataframe
        hulls = pd.concat(
            [
                hulls,
                gpd.GeoDataFrame(
                    {
                        "num_tweets": len(points),
                        "area_km2": Polygon(points[hull.vertices]).area / 10**6,
                        "start_time_ts": start_time,
                        "geometry": Polygon(points[hull.vertices]),
                    },
                    index=[cluster],
                ),
            ]
        )
        # Reset the index
        hulls.index = range(0, len(hulls))
        # Set the CRS of the geodataframe
        hulls.set_crs(epsg=2154, inplace=True)
        # Calculate the area of the hulls
        hulls["area_km2"] = round(hulls.area / 10**6, 2)
    return hulls
