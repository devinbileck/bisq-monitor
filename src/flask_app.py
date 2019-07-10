import json

import numpy as np
import pandas as pd
import plotly
import plotly.graph_objs as go
from flask import Flask, render_template, Response
from flask.views import View


class EndpointAction(object):

    def __init__(self, action):
        self.action = action
        self.response = Response(status=200, headers={})

    def __call__(self, *args):
        self.action()
        return self.response


class FlaskApp(object):

    def __init__(self, name):
        self.app = Flask(name)
        #self.add_endpoint(endpoint='/', endpoint_name='root', handler=self.index)
        self.app.add_url_rule('/', view_func=Dashboard.as_view('dashboard'))

    def run(self):
        self.app.run()

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None, view=None):
        self.app.add_url_rule(endpoint, endpoint_name, EndpointAction(handler), view_func=view)


def create_plot():
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
    graph_json = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return graph_json


class Dashboard(View):

    def dispatch_request(self):
        bar = create_plot()
        return render_template('index.html', plot=bar)

