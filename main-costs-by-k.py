from model import HubModel
import plotly.graph_objects as go

costs = []

hb = HubModel(K=1)
hb.create_objective()
hb.create_constraints()
hb.optimize_model()
costs.append(hb.calculate_num_intermediate_hubs())

hb2 = HubModel(K=2)
hb2.create_objective()
hb2.create_constraints()
hb2.optimize_model()
costs.append(hb2.calculate_num_intermediate_hubs())

hb4 = HubModel(K=4)
hb4.create_objective()
hb4.create_constraints()
hb4.optimize_model()
costs.append(hb4.calculate_num_intermediate_hubs())

hb6 = HubModel(K=6)
hb6.create_objective()
hb6.create_constraints()
hb6.optimize_model()
costs.append(hb6.calculate_num_intermediate_hubs())

x_values = [str(x) for x in [1, 2, 4, 6]]

# Creating the line plot using Plotly
fig = go.Figure(data=go.Scatter(x=x_values, y=costs, mode='lines+markers', marker=dict(symbol='square')))

# Update the layout
fig.update_layout(
    title='Total Operational Overhead Cost vs the number of hubs',
    xaxis_title='Number of Hubs (K)',
    yaxis_title='Total Operational Overhead Cost'
)

# Display the figure
fig.show()
