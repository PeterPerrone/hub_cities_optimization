import gurobipy as gp
from functions import *

VALID_SIZES = ["small", "med", "large"]


class HubModel:

    def __init__(self, K=2, alpha=0.75, size="small", model_name="Hub-Spoke"):
        if size not in VALID_SIZES:
            raise Exception(f"Only sizes of {VALID_SIZES} are allowed. You provided {size}.")
        self.K = K
        self.alpha = alpha

        self.df_cities, self.df_packages = load_dataframes(size)
        self.cities = self.df_cities.id.to_list()
        self.N = len(self.cities)

        self.model = Model(model_name)
        self.f = extract_packages(self.df_packages, self.N)
        self.d = extract_distances(self.df_cities, self.cities)

        self.Y = None
        self.Z = None

    def create_objective(self):
        self.Y = self.model.addVars(self.N, self.N, vtype=GRB.BINARY, name="Y")
        self.Z = m.addVars(self.N, self.N, self.N, self.N, vtype=GRB.BINARY, name="Z")

        obj = gp.LinExpr()
        for s in self.cities:
            for a in self.cities:
                for h1 in self.cities:
                    for h2 in self.cities:
                        obj += self.f[(s, a)] * self.Z[s, h1, a, h2] * (self.d[(s, h1)] + self.alpha * self.d[(h1, h2)] + self.d[(h2, a)])
        self.model.setObjective(obj, GRB.MINIMIZE)

    def create_constraints(self):
        pass

    def optimize_model(self):
        pass
