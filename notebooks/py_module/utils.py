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


def plot_space_time_cube(tweets, eps1_terrain, eps2):
    # Create figure with 3D projected axis
    fig, ax = plt.subplots(subplot_kw={"projection": "3d"}, figsize=(5, 5))

    # Figure properties
    fig.tight_layout(pad=4)
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

    ax.get_figure().savefig(
        f"./images/st_dbscan/st_dbscan_cube_eps1_{eps1_terrain / 1_000:.0f}_km_eps2_{int(eps2 / 60)}_min.png",
        dpi=300,
        facecolor=ax.get_figure().get_facecolor(),
        edgecolor="none",
    )


def plot_hulls(tweets, hulls, eps1_terrain, eps2, min_samples):
    # Read France geojson
    basemap = gpd.read_file(filename="../data/france.geojson")
    basemap = basemap.to_crs("EPSG:2154")

    fig2, base = plt.subplots(figsize=(6, 6))
    # Plot base map
    basemap.plot(ax=base, color="#F2E7DC", figsize=(7, 7), linewidth=0)
    base.set_facecolor("#818274")
    base.get_figure().patch.set_facecolor("#22272e")

    # Plot tweets with color based on cluster
    for cluster in tweets.index.get_level_values(0).unique():
        # Number of tweets in cluster
        num_tweets = len(tweets[tweets.index.get_level_values(0) == cluster])
        # Check whether cluster id exists in hulls
        if cluster in hulls.index.values or cluster == -1:
            print("Cluster {}: {} tweets".format(cluster, num_tweets))
            tweets[tweets.index.get_level_values(0) == cluster].plot(
                ax=base,
                markersize=6 if cluster == -1 else 10,
                label="Noise" if cluster == -1 else "Cluster {}".format(cluster),
                marker="x" if cluster != -1 else "+",
                color="#161819" if cluster == -1 else "C{}".format(cluster),
                linewidth=0.5 if cluster == -1 else 0.8,
            )

    for cluster in hulls.index:
        hulls[hulls.index == cluster].plot(
            ax=base,
            alpha=0.3,
            color="C{}".format(cluster),
            edgecolor="C{}".format(cluster),
            linewidth=1,
        )

    # Set title
    base.set_title(
        "ST-DBSCAN Clustering of Teil Quake Tweets",
        fontsize=16,
        weight="medium",
        color="white",
        pad=10,
    )

    # Set legend
    base.legend(
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
    # bbox_to_anchor=(1.23, 1.01

    # Add grid
    base.grid(color="#161819", linestyle="-", linewidth=0.2, alpha=0.3)

    # Change tick labels
    m2km = lambda x, _: f"{x/1000:g}"
    base.xaxis.set_major_formatter(m2km)
    base.yaxis.set_major_formatter(m2km)

    # Set axis labels
    base.set_xlabel("X (km)", fontsize=7, labelpad=5, color="white")
    base.set_ylabel("Y (km)", fontsize=7, labelpad=5, color="white")

    # Set axis ticks color
    base.tick_params(axis="x", colors="white")
    base.tick_params(axis="y", colors="white")

    textstr = "\n".join(
        (
            r"$eps1=%.0f$ km" % (eps1_terrain / 1_000,),
            r"$eps2=%d$ min" % (eps2,),
            r"$min_{samples}=%d$ tweets" % (min_samples,),
        )
    )

    # these are matplotlib.patch.Patch properties
    props = dict(facecolor="white", edgecolor="#22272e")

    # place a text box in upper left in axes coords
    base.text(
        0.02,
        0.98,
        textstr,
        transform=base.transAxes,
        fontsize=8,
        verticalalignment="top",
        bbox=props,
        color="#22272e",
    )

    base.get_figure().savefig(
        f"./images/st_dbscan/st_dbscan_eps1_{eps1_terrain / 1_000:.0f}_km_eps2_{int(eps2 / 60)}_min.png",
        dpi=300,
        bbox_inches="tight",
        facecolor=base.get_figure().get_facecolor(),
        edgecolor="none",
    )
