from gurobipy import Model, GRB
import pandas as pd
import numpy as np


# Guaranteed to get a valid size, since checked before calling this method
def load_dataframes(size="small"):
    """
    :param size: Size of dataframe either small, med or large
    :return: 2 dataframes containing cities and packages info
    """
    df_cities = pd.read_csv(f"files/cities_{size}.csv")
    df_packages = pd.read_csv(f"files/packages_{size}.csv")
    return df_cities, df_packages


def extract_packages(packages, N):
    """
    :param packages: df_packages Dataframe
    :param N: Number of cities
    :return: Dictionary of packages values for each city combination
    """
    packages = packages.sort_values(["origin", "destination"])
    pkgs = {(row['origin'], row['destination']): row['packages'] for _, row in packages.iterrows()}
    # for i in range(N):
    #     for j in range(N):
    #         if (i, j) not in pkgs:
    #             pkgs[(i, j)] = 0
    return pkgs


def extract_distances(df_cities, cities):
    """
    :param df_cities: cities dataframe
    :param cities: list of cities
    :return: dist dict containing distance for each pair of cities
    """
    def compute_dist(city1_row, city2_row):
        city1_lat = city1_row.lat.item()
        city1_lon = city1_row.lon.item()
        city2_lat = city2_row.lat.item()
        city2_lon = city2_row.lon.item()
        return np.sqrt((city1_lat - city2_lat) ** 2 + (city1_lon - city2_lon) ** 2)

    dists = {}
    for i, city1 in enumerate(cities):
        city1_row = df_cities[df_cities.id == city1]
        for city2 in cities[i:]:
            city2_row = df_cities[df_cities.id == city2]
            if (city1, city2) not in dists:
                curr_dist = compute_dist(city1_row, city2_row)
                dists[(city1, city2)] = curr_dist
                dists[(city2, city1)] = curr_dist
    return dists

