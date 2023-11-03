from model import HubModel
from plots import Plots
from functions import save_hub_model, load_hub_model

hb = HubModel()
hb.create_objective()
hb.create_constraints()
hb.optimize_model()
hb.save_model('hub-model-mat')
new_hb = HubModel.load_model()
# save_hub_model("hub-k2", hb)
cost = hb.calculate_costs()
cost2 = new_hb.calculate_costs()
hb.get_hubs()
new_hb.get_hubs()
# P = Plots(hb)
# P.plot_hub_and_cities()
b=1
P = Plots(hb)
P.plot_hub_and_cities_plotly()
