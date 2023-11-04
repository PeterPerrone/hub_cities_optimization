from model import HubModel
import plotly.graph_objects as go

costs = [.5, 1, 5, 10, 100]
# costs = [1]
obj_value = []


for c1 in costs:
    print(f"TESTING WITH COST {c1}")
    hb = HubModel(c=c1, model_name=f"Hub-Spoke-K{2}-C{c1}")
    hb.create_objective()
    hb.create_constraints()
    hb.optimize_model()
    hb.save_model()
    obj_value.append(hb.calculate_costs())

# Creating the line plot using Plotly
fig = go.Figure(data=go.Scatter(x=[str(x) for x in costs], y=costs, mode='lines+markers', marker=dict(symbol='square')))

# Update the layout
fig.update_layout(
    title='Objective Value vs different non-negative values of c',
    xaxis_title='Values of c (cost to handle one package at each intermediate hub)',
    yaxis_title='Objective Value'
)

# Display the figure
fig.show()
