# clustering-tweets-earthquake

This repository contains the code for testing different clustering algorithms on tweets related to the 2019 Teil earthquake.

## Clustering algorithms

- KMeans : [sklearn.cluster.KMeans](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html#sklearn.cluster.KMeans)
- MiniBatchKMeans : [sklearn.cluster.MiniBatchKMeans](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.MiniBatchKMeans.html#sklearn.cluster.MiniBatchKMeans)
- DBSCAN : [sklearn.cluster.DBSCAN](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html#sklearn.cluster.DBSCAN)
- ST-DBSCAN : [ST-DBSCAN](https://github.com/eren-ck/st_dbscan)

## Twitter API

The Twitter API is used to get tweets related to the earthquake from the last 7 days.

### Tweepy

The [Tweepy](https://www.tweepy.org/) library is used to access the Twitter API.

```shell
pip install tweepy==3.7
```

### Keys

Change the following variables in the `notebooks/keys.py.example` file:

- `consumer_key`
- `consumer_secret`
- `access_token`
- `access_token_secret`
