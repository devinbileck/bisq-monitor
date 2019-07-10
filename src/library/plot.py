import json

import numpy as np
import pandas as pd
import plotly
import plotly.graph_objs as go


def create_plot(feature):
    if feature == 'Bar':
        n = 40
        x = np.linspace(0, 1, n)
        y = np.random.randn(n)
        df = pd.DataFrame({'x': x, 'y': y})  # creating a sample dataframe
        data = [
            go.Bar(
                x=df['x'],  # assign x as the dataframe column 'x'
                y=df['y']
            )
        ]
    else:
        n = 1000
        random_x = np.random.randn(n)
        random_y = np.random.randn(n)

        # Create a trace
        data = [go.Scatter(
            x=random_x,
            y=random_y,
            mode='markers'
        )]
    graph_json = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return graph_json
