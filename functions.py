from gurobipy import Model, GRB
import pandas as pd
import numpy as np

df_cities = pd.read_csv("files/cities_small.csv")
df_packages = pd.read_csv("files/packages_small.csv")

cities = df_cities.id.to_list()
N = len(cities)


def extract_packages(packages):
    packages = packages.sort_values(["origin", "destination"])
    pkgs = {(row['origin'], row['destination']): row['packages'] for _, row in packages.iterrows()}
    for i in range(N):
        for j in range(N):
            if (i, j) not in pkgs:
                pkgs[(i, j)] = 0
    return pkgs


def extract_distances(cities):
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


# Initialize a new model
m = Model()

# Define parameters
K = 2

# Decision variables
Y = m.addVars(N, N, vtype=GRB.BINARY, name="Y")
Z = m.addVars(N, N, N, N, vtype=GRB.BINARY, name="Z")

# Objective function
f = extract_packages(df_packages)
d = extract_distances(cities)
alpha = 0.75

obj = sum(f[(s, a)] for s in range(N) for a in range(N)) + \
      sum(Z[s, h1, a, h2] * (d[(s, h1)] + alpha * d[(h1, h2)] + d[(h2, a)])
          for s in range(N) for a in range(N) for h1 in range(N) for h2 in range(N))

m.setObjective(obj, GRB.MINIMIZE)

# Constraints
for i in range(N):
    m.addConstr(Y.sum(i, '*') <= K, "hubs_constraint")

    m.addConstr(Y.sum(i, '*') == 1, "city_to_hub_constraint")

    m.addConstr(Z.sum(i, '*', '*', '*') == 1, "both_constraints")

for i in range(N):
    for j in range(N):
        for k in range(N):
            for l in range(N):
                m.addConstr(Z[i, j, k, l] <= Y[i, j], "c1")
                m.addConstr(Z[i, j, k, l] <= Y[k, l], "c2")
                m.addConstr(Z[i, j, k, l] <= Y[i, j] + Y[k, l] - 1, "c3")
                m.addConstr(Z[i, j, k, l] >= 0, "non_negativity")

# Solve the model
m.optimize()

# Extract the results if needed
if m.status == GRB.Status.OPTIMAL:
    for i in range(N):
        for j in range(N):
            print(f"Y[{i},{j}] = {Y[i, j].x}")

    for i in range(N):
        for j in range(N):
            for k in range(N):
                for l in range(N):
                    print(f"Z[{i},{j},{k},{l}] = {Z[i, j, k, l].x}")
