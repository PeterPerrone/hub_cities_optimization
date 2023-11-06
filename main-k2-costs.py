from model import HubModel
import plotly.graph_objects as go
from plots import Plots
import os

costs = [.5, 1, 5, 10, 20, 30, 40, 50, 100]
obj_value = []
overhead_costs = []
total_distances = []

"""for c1 in costs:
    print(f"TESTING WITH COST {c1}")
    hb = HubModel(c=c1, model_name=f"Hub-Spoke-K{2}-C{c1}")
    hb.create_objective()
    hb.create_constraints()
    hb.optimize_model()
    hb.save_model()"""

for c1 in costs:
    print(f"TESTING WITH COST {c1}")
    name = f"Hub-Spoke-K{2}-C{c1}"
    if os.path.exists(f"{name}.mps"):
        hb = HubModel.load_model(name)
    else:
        hb = HubModel(K=2, model_name=name)
        hb.create_objective()
        hb.create_constraints()
        hb.optimize_model()
        hb.save_model()
    obj_value.append(hb.get_obj_value())
    overhead_costs.append(hb.total_cost())
    total_distances.append(hb.total_distance_travelled_by_all_packages())
    P = Plots(hb)
    P.plot_hub_and_cities_plotly()

# Create the figure
fig = go.Figure()

# Add the objective value line
fig.add_trace(go.Scatter(x=[str(x) for x in costs], y=obj_value, mode='lines+markers', name='Objective Value',
                         marker=dict(symbol='square')))

# Add the overhead costs line
fig.add_trace(go.Scatter(x=[str(x) for x in costs], y=overhead_costs, mode='lines+markers', name='Overhead Costs',
                         marker=dict(symbol='circle')))

# Add the total distances line
fig.add_trace(go.Scatter(x=[str(x) for x in costs], y=total_distances, mode='lines+markers', name='Total Distances',
                         marker=dict(symbol='diamond')))

# Update the layout
fig.update_layout(
    title='Metrics vs Different Non-negative Values of c',
    xaxis_title='Values of c (cost to handle one package at each intermediate hub)',
    yaxis_title='Metrics Value',
    legend_title='Metric'
)

# Display the figure
fig.show()
