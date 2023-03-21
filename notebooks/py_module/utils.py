import datetime
import matplotlib
import pandas as pd
import geopandas as gpd
import matplotlib as mpl
from cycler import cycler
import matplotlib.pyplot as plt
from prettytable import PrettyTable
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


def plot_tweets_hulls(tweets, hulls, eps1, eps2, min_samples):
    # Create gridspec for 2 subplots
    GS = matplotlib.gridspec.GridSpec(1, 2)
    fig = plt.figure(figsize=(10, 6))
    fig.patch.set_facecolor("white")

    # Set title
    plt.figtext(
        0.5,
        0.92,
        "\n".join(
            (
                r"Extraction agnostique de la zone de ressenti",
                r"du séisme de 2019 à Teil",
            )
        ),
        ha="center",
        va="top",
        fontsize=15,
        color="black",
        weight="heavy",
    )

    # Create subplots
    axes = fig.add_subplot(GS[0], projection="rectilinear"), fig.add_subplot(
        GS[1], projection="3d"
    )

    # Set background color
    axes[0].set_facecolor("#818274")
    axes[1].set_facecolor("white")

    # Set formatter for axis ticks
    m2km = lambda x, _: f"{x/1000:g}"
    axes[0].xaxis.set_major_formatter(m2km)
    axes[0].yaxis.set_major_formatter(m2km)

    axes[1].xaxis.set_major_formatter(m2km)
    axes[1].yaxis.set_major_formatter(m2km)

    # Set axis labels
    axes[0].set_xlabel("X (km)", fontsize=7, labelpad=5, color="black")
    axes[0].set_ylabel("Y (km)", fontsize=7, labelpad=5, color="black")

    axes[1].set_xlabel("X (km)", fontsize=7, labelpad=5, color="black")
    axes[1].set_ylabel("Y (km)", fontsize=7, labelpad=5, color="black")
    axes[1].set_zlabel("Temps cumulé (min)", fontsize=7, labelpad=5, color="black")

    # Set axis ticks color
    axes[0].tick_params(axis="x", colors="black", labelsize=7)
    axes[0].tick_params(axis="y", colors="black", labelsize=7)

    axes[1].tick_params(axis="x", colors="black", labelsize=7)
    axes[1].tick_params(axis="y", colors="black", labelsize=7)
    axes[1].tick_params(axis="z", colors="black", labelsize=7)

    # Select tweets without noise
    no_noise_tweets = tweets[tweets.index.get_level_values(0) != -1]

    for cluster in set(no_noise_tweets.index.get_level_values(0)):
        # Select tweets in cluster
        no_noise_tweetscluster = no_noise_tweets[
            no_noise_tweets.index.get_level_values(0) == cluster
        ]
        # Plot tweets in cluster
        axes[1].scatter3D(
            no_noise_tweetscluster["x_m"],
            no_noise_tweetscluster["y_m"],
            no_noise_tweetscluster["cumulative_time_sec"] / 60,
            s=2,
            color="C{}".format(cluster),
            label="Noise" if cluster == -1 else "Cluster {}".format(cluster),
        )

    # Plot basemap
    basemap = gpd.read_file(filename="../data/france.geojson")
    basemap.plot(ax=axes[0], color="#F2E7DC", linewidth=0)

    # Plot tweets with color based on cluster
    cluster_ls = []
    num_tweets_ls = []
    for cluster in tweets.index.get_level_values(0).unique():
        # Number of tweets in cluster
        num_tweets = len(tweets[tweets.index.get_level_values(0) == cluster])
        # Check whether cluster id exists in hulls
        if cluster in hulls.index.values or cluster == -1:
            cluster_ls.append(f"Cluster {cluster}")
            num_tweets_ls.append(num_tweets)
            tweets[tweets.index.get_level_values(0) == cluster].plot(
                ax=axes[0],
                markersize=6 if cluster == -1 else 10,
                label="Noise" if cluster == -1 else "Cluster {}".format(cluster),
                marker="x" if cluster != -1 else "+",
                color="#161819" if cluster == -1 else "C{}".format(cluster),
                linewidth=0.5 if cluster == -1 else 0.8,
            )

    # Combine cluster ids and number of tweets in a list
    result = [cluster_ls, num_tweets_ls]
    table = PrettyTable(result[0])
    table.add_row(result[1])
    print(table)

    for cluster in hulls.index:
        hulls[hulls.index == cluster].plot(
            ax=axes[0],
            alpha=0.3,
            color="C{}".format(cluster),
            edgecolor="C{}".format(cluster),
            linewidth=1,
        )

    # Add grid
    axes[0].grid(color="#161819", linestyle="-", linewidth=0.2, alpha=0.3)

    # Add text box
    textstr = "\n".join(
        (
            r"$eps1=%.0f$ km" % (eps1 / 1_000,),
            r"$eps2=%d$ min" % (int(eps2 / 60),),
            r"$min_{samples}=%d$ tweets" % (min_samples,),
        )
    )

    props = dict(facecolor="white", edgecolor="#22272e")

    axes[0].text(
        -1.16,
        0.93,
        textstr,
        transform=axes[1].transAxes,
        fontsize=8,
        verticalalignment="top",
        bbox=props,
        color="#22272e",
    )

    # Legend
    axes[0].legend(
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

    axes[1].legend(
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

    # Save figure
    plt.savefig(
        fname=f"./images/st_dbscan/st_dbscan_eps1_{int(eps1 / 1_000)}_km_eps2_{int(eps2 / 60)}_min_{min_samples}.png",
        dpi=300,
        facecolor=fig.get_facecolor(),
        pad_inches=0.3,
        bbox_inches="tight",
    )

    plt.show()
