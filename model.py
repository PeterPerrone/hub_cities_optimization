import gurobipy as gp
from functions import *

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

        self.model = gp.Model(model_name)
        self.f = extract_packages(self.df_packages, self.N)
        self.d = extract_distances(self.df_cities, self.cities)

        self.Y = None
        self.Z = None

    @classmethod
    def load_model(cls, file_to_load="hub-model", model_name="Hub-Spoke"):
        obj = cls.__new__(cls)
        with open(f"saved_models/{file_to_load}.pkl", 'rb') as file:
            loaded_attributes = pickle.load(file)
        obj.__dict__.update(loaded_attributes)

        obj.model = gp.read(f"saved_models/{file_to_load}.mps")
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
                    self.c * gp.quicksum(self.Z[s, h1, a, h2] * (2 - self.Y[h1, s] - self.Y[h1, h2] - self.Y[h2, a])
                                         for h1 in self.cities for h2 in self.cities)
            ) for (s, a), pkgs in self.f.items())
            # obj = gp.quicksum(pkgs *
            #                   gp.quicksum(self.Z[s, h1, a, h2] * (
            #                           (
            #                               self.d[(s, h1)] +
            #                               self.alpha * self.d[(h1, h2)] +
            #                               self.d[(h2, a)]
            #                           ) +
            #                           (
            #                               self.c * (2 - self.Y[h1, s] - self.Y[h1, h2] - self.Y[h2, a])
            #                           )
            #                   ) for h1 in self.cities for h2 in self.cities)
            #                   for (s, a), pkgs in self.f.items())
        else:
            obj = gp.quicksum(pkgs * (
                gp.quicksum(self.Y[s, h1] * self.d[(s, h1)] for h1 in self.cities) +
                gp.quicksum(self.Y[a, h2] * self.d[(a, h2)] for h2 in self.cities) +
                self.alpha * gp.quicksum(self.Z[s, h1, a, h2] * self.d[(h1, h2)] for h1 in self.cities for h2 in self.cities)
            ) for (s, a), pkgs in self.f.items())

        # obj = gp.LinExpr()
        # for (s, a), pkgs in self.f.items():
        #     for h1 in self.cities:
        #         for h2 in self.cities:
        #             if self.c:
        #                 obj += pkgs * self.Z[s, h1, a, h2] * (
        #                         (
        #                                 self.d[(s, h1)] +
        #                                 self.alpha * self.d[(h1, h2)]
        #                                 + self.d[(h2, a)]
        #                         ) +
        #                         (
        #                                 self.c * (2 - self.Y[h1, s] - self.Y[h1, h2] - self.Y[h2, a])
        #                         )
        #                 )
        #             else:
        #                 obj += pkgs * self.Z[s, h1, a, h2] * \
        #                        (self.d[(s, h1)] + self.alpha * self.d[(h1, h2)] + self.d[(h2, a)])
        self.model.setObjective(obj, GRB.MINIMIZE)

    def create_constraints(self):
        # Less than K hubs
        self.model.addConstr(gp.quicksum(self.Y[i, i] for i in self.cities) <= self.K, name="K-hubs")

        # City has only one hub
        for i in self.cities:
            self.model.addConstr(gp.quicksum(self.Y[i, H] for H in self.cities) == 1, name=f"city_{i} 1 hub")

        # Each assigned hub (from a city) is actually a hub
        for i in self.cities:
            for H in self.cities:
                self.model.addConstr(self.Y[i, H] - self.Y[H, H] <= 0, name=f"city_{i} hub_{H} valid")

        # Linearization constraints for Z
        for i in self.cities:
            for j in self.cities:
                for k in self.cities:
                    for l in self.cities:
                        self.model.addConstr(self.Z[i, j, k, l] <= self.Y[i, j], name=f"Linearization at most Y_{i, j}")
                        self.model.addConstr(self.Z[i, j, k, l] <= self.Y[k, l], name=f"Linearization at most Y_{k, l}")
                        self.model.addConstr(self.Z[i, j, k, l] >= self.Y[i, j] + self.Y[k, l] - 1,
                                             name=f"Linearization at least Y_{i, j} and Y_{k, l} - 1")

    def optimize_model(self):
        self.model.optimize()
        print(f'Optimal objective: {self.model.ObjVal}')
        self.model.write('model.sol')

    def get_obj_value(self):
        return self.model.ObjVal

    def get_hubs(self):
        for i in self.cities:
            if self.Y[i, i].X:
                print(f"City {i} is a hub")

    def calculate_costs(self):
        total_c = 0
        for (s, a), pkgs in self.f.items():
            for h1 in self.cities:
                for h2 in self.cities:
                    total_c += self.Z[s, h1, a, h2].X * pkgs * (
                                2 - self.Y[h1, s].X - self.Y[h1, h2].X - self.Y[h2, a].X)
        print(f"Cost for this model is {total_c}*c")
        return total_c

    def cost_per_package(self):
        total_cost = self.calculate_costs()
        return total_cost / sum(self.f.values())

    def save_model(self, name="hub-model"):
        attributes_to_save = {
            'K': self.K,
            'alpha': self.alpha,
            'df_cities': self.df_cities,
            'cities': self.cities,
            'N': self.N,
            'f': self.f,
            'd': self.d,
        }

        with open(f"saved_models/{name}.pkl", 'wb') as file:
            pickle.dump(attributes_to_save, file)

        self.model.write(f"saved_models/{name}.mps")


if __name__ == "__main__":
    b = 1
