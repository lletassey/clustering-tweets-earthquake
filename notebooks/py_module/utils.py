import datetime
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
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
        # Set the CRS of the geodataframe
        hulls.set_crs(epsg=2154, inplace=True)
        # Calculate the area of the hulls
        hulls["area_km2"] = round(hulls.area / 10**6, 2)
    return hulls


def plot_space_time_cube(tweets):
    # Create figure with 3D projected axis
    fig, ax = plt.subplots(subplot_kw={"projection": "3d"}, figsize=(5, 5))

    # Figure properties
    fig.tight_layout(pad=3)
    fig.set_facecolor("white")

    m2km = lambda x, _: f"{x/1000:g}"
    ax.xaxis.set_major_formatter(m2km)
    ax.yaxis.set_major_formatter(m2km)

    # Set axis labels
    ax.set_xlabel("X (km)", fontsize=7, labelpad=5, color="black")
    ax.set_ylabel("Y (km)", fontsize=7, labelpad=5, color="black")
    ax.set_zlabel("Temps cumulé (min)", fontsize=7, labelpad=5, color="black")

    # Set axis ticks color
    ax.tick_params(axis="x", colors="black", labelsize=7)
    ax.tick_params(axis="y", colors="black", labelsize=7)
    ax.tick_params(axis="z", colors="black", labelsize=7)

    # Select tweets without noise
    no_noise_tweets = tweets[tweets.index.get_level_values(0) != -1]

    for cluster in set(no_noise_tweets.index.get_level_values(0)):
        # Select tweets in cluster
        no_noise_tweetscluster = no_noise_tweets[
            no_noise_tweets.index.get_level_values(0) == cluster
        ]
        # Plot tweets in cluster
        ax.scatter3D(
            no_noise_tweetscluster["x_m"],
            no_noise_tweetscluster["y_m"],
            no_noise_tweetscluster["cumulative_time_sec"] / 60,
            s=2,
            color="C{}".format(cluster),
            label="Noise" if cluster == -1 else "Cluster {}".format(cluster),
        )

    # Axis properties
    ax.set_facecolor("white")
    ax.set_title(
        "ST-DBSCAN Clustering of Teil Quake Tweets",
        fontsize=11,
        weight="medium",
        color="black",
        pad=10,
    )
    ax.legend(
        loc="best",
        fontsize=9,
        labelcolor="#22272e",
        markerscale=2,
        facecolor="white",
        title_fontsize=14,
        fancybox=False,
        framealpha=1,
        edgecolor="#22272e",
    )

    # Save fig
    plt.savefig("st_dbscan.png", dpi=300, bbox_inches="tight")
    plt.savefig(
        f"./images/st_dbscan/st_dbscan_3d.png",
        dpi=300,
        facecolor=ax.get_figure().get_facecolor(),
        edgecolor="none",
    )

    plt.show()
