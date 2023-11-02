# import plotly.express as px
import matplotlib.pyplot as plt
from model import HubModel


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

