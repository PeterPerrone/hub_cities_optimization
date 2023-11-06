from model import HubModel
from plots import Plots
import os

for K in [1, 2, 4, 6, 8, 10, 12]:
    name = f"Hub-Spoke-K{K}"
    if os.path.exists(f"{name}.mps"):
        hb = HubModel.load_model(name)
    else:
        hb = HubModel(K=K, model_name=name)
        hb.create_objective()
        hb.create_constraints()
        hb.optimize_model()
        hb.save_model()
    plotter = Plots(hb)
    plotter.plot_hub_and_cities_plotly()