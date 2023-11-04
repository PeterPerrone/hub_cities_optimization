import gurobipy as gp
from functions import *
import pickle

VALID_SIZES = ["small", "med", "large"]


class HubModel:

    def __init__(self, K=2, alpha=0.75, size="small", model_name="Hub-Spoke", c=0):
        if size not in VALID_SIZES:
            raise Exception(f"Only sizes of {VALID_SIZES} are allowed. You provided {size}.")
        self.K = K
        self.alpha = alpha

        self.df_cities, self.df_packages = load_dataframes(size)
        self.cities = self.df_cities.id.to_list()
        self.N = len(self.cities)

        self.c = c

        self.model_name = model_name
        self.model = gp.Model(self.model_name)
        self.f = extract_packages(self.df_packages, self.N)
        self.d = extract_distances(self.df_cities, self.cities)

        self.Y = None
        self.Z = None

    @classmethod
    def load_model(cls, file_to_load="Hub-Spoke-K2"):
        obj = cls.__new__(cls)
        with open(f"saved_models/{file_to_load}.pkl", 'rb') as file:
            loaded_attributes = pickle.load(file)
        obj.__dict__.update(loaded_attributes)

        obj.model = gp.read(f"saved_models/{file_to_load}.mps")
        obj.model.read(f"saved_models/{file_to_load}.sol")
        obj.model.params.TimeLimit = 1
        obj.model.optimize()
        obj.Y = gp.tupledict({(i, j): obj.model.getVarByName(f'Y[{i},{j}]') for i in obj.cities for j in obj.cities})
        obj.Z = gp.tupledict(
            {(i, j, k, l): obj.model.getVarByName(f'Z[{i},{j},{k},{l}]') for i in obj.cities for j in obj.cities for k
             in obj.cities for l in obj.cities})
        return obj

    def create_objective(self):
        self.Y = self.model.addVars(self.N, self.N, vtype=GRB.BINARY, name="Y")
        self.Z = self.model.addVars(self.N, self.N, self.N, self.N, vtype=GRB.BINARY, name="Z")

        if self.c:
            obj = gp.quicksum(pkgs * (
                    gp.quicksum(self.Y[s, h1] * self.d[(s, h1)] for h1 in self.cities) +
                    gp.quicksum(self.Y[a, h2] * self.d[(a, h2)] for h2 in self.cities) +
                    self.alpha * gp.quicksum(self.Z[s, h1, a, h2] * self.d[(h1, h2)]
                                             for h1 in self.cities for h2 in self.cities) +
                    self.c * (2 - self.Y[s, s] - self.Y[a, a] - gp.quicksum(self.Z[s, h, a, h] for h in self.cities))
            ) for (s, a), pkgs in self.f.items())

        else:
            obj = gp.quicksum(pkgs * (
                gp.quicksum(self.Y[s, h1] * self.d[(s, h1)] for h1 in self.cities) +
                gp.quicksum(self.Y[a, h2] * self.d[(a, h2)] for h2 in self.cities) +
                self.alpha * gp.quicksum(self.Z[s, h1, a, h2] * self.d[(h1, h2)]
                                         for h1 in self.cities for h2 in self.cities)
            ) for (s, a), pkgs in self.f.items())

        self.model.setObjective(obj, GRB.MINIMIZE)

    def create_constraints(self):
        # Less than K hubs
        self.model.addConstr(gp.quicksum(self.Y[i, i] for i in self.cities) <= self.K, name="K-hubs")

        # City has only one hub
        for i in self.cities:
            self.model.addConstr(gp.quicksum(self.Y[i, H] for H in self.cities) == 1, name=f"city_{i}-1hub")

        # Each assigned hub (from a city) is actually a hub
        for i in self.cities:
            for H in self.cities:
                self.model.addConstr(self.Y[i, H] - self.Y[H, H] <= 0, name=f"city_{i}-hub_{H}-valid")

        # Linearization constraints for Z
        for i in self.cities:
            for j in self.cities:
                for k in self.cities:
                    for l in self.cities:
                        self.model.addConstr(self.Z[i, j, k, l] <= self.Y[i, j], name=f"Linearization-at-most-Y_{i, j}")
                        self.model.addConstr(self.Z[i, j, k, l] <= self.Y[k, l], name=f"Linearization-at-most-Y_{k, l}")
                        self.model.addConstr(self.Z[i, j, k, l] >= self.Y[i, j] + self.Y[k, l] - 1,
                                             name=f"Linearization-at-least-Y_{i, j}-and-Y_{k, l}_-_1")

    def optimize_model(self, fname=None):
        if not fname:
            fname = self.model_name
        self.model.optimize()
        print(f'Optimal objective: {self.model.ObjVal}')
        self.model.write(f'saved_models/{fname}.sol')

    def get_obj_value(self):
        return self.model.ObjVal

    def get_hubs(self):
        for i in self.cities:
            if self.Y[i, i].X:
                print(f"City {i} is a hub")

    def calculate_num_intermediate_hubs(self):
        total_int_hubs = 0
        for (s, a), pkgs in self.f.items():
            flow_int_hub = 2 - self.Y[s, s].X - self.Y[a, a].X
            for h in self.cities:
                flow_int_hub -= self.Z[s, h, a, h].X
            total_int_hubs += pkgs * flow_int_hub
        return total_int_hubs

    def avg_num_intermediate_hubs(self):
        total_int_hubs = self.calculate_num_intermediate_hubs()
        return total_int_hubs / sum(self.f.values())

    def total_cost(self):
        return self.c * self.calculate_num_intermediate_hubs()

    def avg_cost_per_package(self):
        return self.c * self.avg_num_intermediate_hubs()

    def save_model(self, fname=None):
        if not fname:
            fname = self.model_name

        attributes_to_save = {
            'K': self.K,
            'alpha': self.alpha,
            'df_cities': self.df_cities,
            'cities': self.cities,
            'N': self.N,
            'f': self.f,
            'd': self.d,
        }

        with open(f"saved_models/{fname}.pkl", 'wb') as file:
            pickle.dump(attributes_to_save, file)

        self.model.write(f"saved_models/{fname}.mps")


if __name__ == "__main__":
    pass
