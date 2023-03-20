import datetime
import matplotlib
import pandas as pd
import geopandas as gpd
import matplotlib as mpl
from cycler import cycler
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon


# Set up matplotlib rcParams (runtime configuration) for plot color
hulls_colors = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]

mpl.rcParams["axes.prop_cycle"] = cycler(
    "color",
    hulls_colors,
)


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


def plot_cube_hulls(tweets, eps1_terrain, eps2, hulls, min_samples):
    GS = matplotlib.gridspec.GridSpec(1, 2)
    fig = plt.figure(figsize=(10, 6))
    fig.patch.set_facecolor("white")

    plt.figtext(
        0.5,
        0.95,
        "ST-DBSCAN Clustering of Teil Quake Tweets",
        ha="center",
        va="top",
        fontsize=14,
        color="black",
        weight="medium",
    )

    ax_cube, ax_hull = fig.add_subplot(GS[0], projection="3d"), fig.add_subplot(
        GS[1], projection="rectilinear"
    )

    m2km = lambda x, _: f"{x/1000:g}"
    ax_cube.xaxis.set_major_formatter(m2km)
    ax_cube.yaxis.set_major_formatter(m2km)

    # Set axis labels
    ax_cube.set_xlabel("X (km)", fontsize=7, labelpad=5, color="black")
    ax_cube.set_ylabel("Y (km)", fontsize=7, labelpad=5, color="black")
    ax_cube.set_zlabel("Temps cumulé (min)", fontsize=7, labelpad=5, color="black")

    # Set axis ticks color
    ax_cube.tick_params(axis="x", colors="black", labelsize=7)
    ax_cube.tick_params(axis="y", colors="black", labelsize=7)
    ax_cube.tick_params(axis="z", colors="black", labelsize=7)

    # Select tweets without noise
    no_noise_tweets = tweets[tweets.index.get_level_values(0) != -1]

    for cluster in set(no_noise_tweets.index.get_level_values(0)):
        # Select tweets in cluster
        no_noise_tweetscluster = no_noise_tweets[
            no_noise_tweets.index.get_level_values(0) == cluster
        ]
        # Plot tweets in cluster
        ax_cube.scatter3D(
            no_noise_tweetscluster["x_m"],
            no_noise_tweetscluster["y_m"],
            no_noise_tweetscluster["cumulative_time_sec"] / 60,
            s=2,
            color="C{}".format(cluster),
            label="Noise" if cluster == -1 else "Cluster {}".format(cluster),
        )

    # Axis properties
    ax_cube.set_facecolor("white")
    ax_cube.legend(
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

    # Read France geojson
    basemap = gpd.read_file(filename="../data/france.geojson")
    basemap = basemap.to_crs("EPSG:2154")

    # Plot base map
    basemap.plot(ax=ax_hull, color="#F2E7DC", figsize=(7, 7), linewidth=0)
    ax_hull.set_facecolor("#818274")
    ax_hull.get_figure().patch.set_facecolor("white")

    # Plot tweets with color based on cluster
    for cluster in tweets.index.get_level_values(0).unique():
        # Number of tweets in cluster
        num_tweets = len(tweets[tweets.index.get_level_values(0) == cluster])
        # Check whether cluster id exists in hulls
        if cluster in hulls.index.values or cluster == -1:
            print("Cluster {}: {} tweets".format(cluster, num_tweets))
            tweets[tweets.index.get_level_values(0) == cluster].plot(
                ax=ax_hull,
                markersize=6 if cluster == -1 else 10,
                label="Noise" if cluster == -1 else "Cluster {}".format(cluster),
                marker="x" if cluster != -1 else "+",
                color="#161819" if cluster == -1 else "C{}".format(cluster),
                linewidth=0.5 if cluster == -1 else 0.8,
            )

    for cluster in hulls.index:
        hulls[hulls.index == cluster].plot(
            ax=ax_hull,
            alpha=0.3,
            color="C{}".format(cluster),
            edgecolor="C{}".format(cluster),
            linewidth=1,
        )

    # Set legend
    ax_hull.legend(
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

    # Add grid
    ax_hull.grid(color="#161819", linestyle="-", linewidth=0.2, alpha=0.3)

    # Change tick labels
    m2km = lambda x, _: f"{x/1000:g}"
    ax_hull.xaxis.set_major_formatter(m2km)
    ax_hull.yaxis.set_major_formatter(m2km)

    # Set axis labels
    ax_hull.set_xlabel("X (km)", fontsize=7, labelpad=5, color="black")
    ax_hull.set_ylabel("Y (km)", fontsize=7, labelpad=5, color="black")

    # Set axis ticks color
    ax_hull.tick_params(axis="x", colors="black", labelsize=7)
    ax_hull.tick_params(axis="y", colors="black", labelsize=7)

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
    ax_hull.text(
        0.02,
        0.98,
        textstr,
        transform=ax_hull.transAxes,
        fontsize=8,
        verticalalignment="top",
        bbox=props,
        color="#22272e",
    )

    plt.tight_layout(pad=3.0)
    plt.show()
