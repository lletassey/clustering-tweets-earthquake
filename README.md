# clustering-tweets-earthquake

This repository contains the code for testing different clustering algorithms on tweets related to the 2019 Teil earthquake.

## Clustering algorithms

- DBSCAN : [sklearn.cluster.DBSCAN](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html#sklearn.cluster.DBSCAN)
- ST-DBSCAN : [ST-DBSCAN](https://github.com/eren-ck/st_dbscan)

## Twitter API

The Twitter API is used to get tweets related to the earthquake from the last 7 days.

### Requirements

Change the following variables in the `notebooks/keys.py.example` file:

- `consumer_key`
- `consumer_secret`
- `access_token`
- `access_token_secret`
