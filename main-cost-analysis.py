from model import HubModel
from plots import Plots
from functions import compute_p2p_cost
import os

Ks = [1, 2, 4, 6, 8, 10, 12]
costs = range(0, 51, 10)
for K in Ks:
    name = f"Hub-Spoke-K{K}"
    if os.path.exists(f"{name}.mps"):
        hb = HubModel.load_model(name)
    else:
        hb = HubModel(K=K, model_name=f"Hub-Spoke-K{K}")
        hb.create_objective()
        hb.create_constraints()
        hb.optimize_model()
        hb.save_model()
    plotter = Plots(hb)
    plotter.dist_obj_vs_p2p_costs(costs)
    plotter.dist_obj_vs_oh_costs(costs)
