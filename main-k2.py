from model import HubModel
from plots import Plots

hb = HubModel(K=2, model_name="Hub-Spoke-Q2")
hb.create_objective()
hb.create_constraints()
hb.optimize_model()
hb.save_model()
hb.get_hubs()
P = Plots(hb)
P.plot_hub_and_cities_plotly()

