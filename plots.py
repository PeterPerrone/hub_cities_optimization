import matplotlib.pyplot as plt
import plotly.graph_objects as go
from model import HubModel
from functions import compute_p2p_cost


class Plots:

    def __init__(self, model: HubModel):
        self.model = model

    def plot_hub_and_cities(self):
        for city_row in self.model.df_cities.itertuples():
            lat = city_row.lat
            lon = city_row.lon
            i = city_row.id
            hub = self.model.Y[i, i].x == 1
            shape = 'p' if hub else 'o'
            plt.scatter(lon, lat, marker=shape, label=i)

            if hub:
                for city2_row in self.model.df_cities.itertuples():
                    j = city2_row.id
                    if i != j and self.model.Y[j, i].X:
                        lat2 = city2_row.lat
                        lon2 = city2_row.lon
                        plt.plot([lon, lon2], [lat, lat2], linestyle='-', color='red')
                    elif self.model.Y[j, j].X:
                        lat2 = city2_row.lat
                        lon2 = city2_row.lon
                        plt.plot([lon, lon2], [lat, lat2], linestyle='-', color='blue')

        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.legend()
        plt.title("Cities and hub map")
        plt.grid(True)
        plt.show()

    def plot_hub_and_cities_plotly(self):
        # Create figure
        fig = go.Figure()

        # Define colors for hubs, cities, and connections
        city_color = 'LightSkyBlue'
        hub_color = 'Salmon'
        hub_connection_color = 'DarkOrange'  # Color for hub-to-hub connections
        city_hub_connection_color = 'Blue'  # Color for city-to-hub connections

        # Keep track of whether we've added the hub connection to the legend
        hub_connection_legend_added = False
        city_hub_connection_legend_added = False

        # Plot each city
        for city_row in self.model.df_cities.itertuples():
            lat = city_row.lat
            lon = city_row.lon
            i = city_row.id
            hub = self.model.Y[i, i].x == 1
            marker_properties = {
                'size': 12 if hub else 8,  # Bigger size for hubs
                'color': hub_color if hub else city_color,
                'symbol': 'square' if hub else 'circle'  # Square for hubs, circle for cities
            }

            # Add scatter plot for cities/hubs with text labels
            fig.add_trace(go.Scatter(
                x=[lon],
                y=[lat],
                mode='markers+text',
                marker=marker_properties,
                text=[str(i)],
                textposition='bottom center',
                name='Hub' if hub else 'City',
                showlegend=False
            ))

        # Add lines for connections after plotting cities to avoid lines over markers
        for city1_row in self.model.df_cities.itertuples():
            i = city1_row.id
            lat1 = city1_row.lat
            lon1 = city1_row.lon
            hub1 = self.model.Y[i, i].x == 1

            for city2_row in self.model.df_cities.itertuples():
                j = city2_row.id
                if i < j:  # Ensure each pair is only considered once
                    hub2 = self.model.Y[j, j].x == 1
                    connected = (self.model.Y[i, j].x or self.model.Y[j, i].x) or (hub1 and hub2)
                    if connected:
                        lat2 = city2_row.lat
                        lon2 = city2_row.lon
                        # Determine the color of the connection
                        if hub1 and hub2:
                            line_color = hub_connection_color
                            # Add to legend only once for hub connections
                            if not hub_connection_legend_added:
                                fig.add_trace(go.Scatter(
                                    x=[None],
                                    y=[None],
                                    mode='lines',
                                    line=dict(color=line_color),
                                    name='Hub Connection'
                                ))
                                hub_connection_legend_added = True
                        else:
                            line_color = city_hub_connection_color
                            # Add to legend only once for city-to-hub connections
                            if not city_hub_connection_legend_added:
                                fig.add_trace(go.Scatter(
                                    x=[None],
                                    y=[None],
                                    mode='lines',
                                    line=dict(color=line_color),
                                    name='City-Hub Connection'
                                ))
                                city_hub_connection_legend_added = True
                        # Add the line trace for the connection
                        fig.add_trace(go.Scatter(
                            x=[lon1, lon2],
                            y=[lat1, lat2],
                            mode='lines',
                            line=dict(width=1, color=line_color),
                            showlegend=False
                        ))

        # Add legend entries manually
        fig.add_trace(go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            marker=dict(size=10, color=city_color),
            name='City'
        ))

        fig.add_trace(go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            marker=dict(size=10, color=hub_color),
            name='Hub'
        ))

        # Set plot layout
        fig.update_layout(
            title="Cities and Hub Map",
            xaxis_title="Longitude",
            yaxis_title="Latitude",
            showlegend=True,
            legend_title_text='Legend',
            xaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGray'),
            yaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGray')
        )

        # Show figure
        fig.show()

    def dist_obj_vs_p2p_costs(self, costs):
        p2p_cost = compute_p2p_cost(self.model.f, self.model.d)
        int_hubs = self.model.calculate_num_intermediate_hubs()
        overhead_costs = [cost * int_hubs for cost in costs]
        obj = self.model.get_obj_value()
        obj_plus_costs = [oh_cost + obj for oh_cost in overhead_costs]
        plt.plot(costs, overhead_costs, label="overhead-cost hub-spoke")
        plt.plot(costs, obj_plus_costs, label="obj + overhead-cost hub-spoke")
        plt.plot(costs, [p2p_cost] * len(costs), label="point-to-point (dist cost only)")
        plt.xlabel("c")
        plt.ylabel("total overhead costs")
        plt.ticklabel_format(axis='y', style='plain')
        plt.legend()
        plt.title(f"Overhead costs in Hub vs. P2P distance (K={self.model.K})")
        plt.savefig(f"plot_images/dist_cost_p2p_K{self.model.K}")
        plt.show()

    def dist_obj_vs_oh_costs(self, costs):
        int_hubs = self.model.calculate_num_intermediate_hubs()
        overhead_costs = [cost * int_hubs for cost in costs]
        obj = self.model.get_obj_value()
        plt.plot(costs, overhead_costs, label="overhead costs")
        plt.plot(costs, [obj] * len(costs), label="dist objective value")
        plt.xlabel("c")
        plt.ylabel("total costs")
        plt.ticklabel_format(axis='y', style='plain')
        plt.title(f"Overhead Costs vs. Distance Cost in Distance only Obj (K={self.model.K})")
        plt.savefig(f"plot_images/dist_vs_oh_cost_dist_obj_K{self.model.K}")
        plt.show()
