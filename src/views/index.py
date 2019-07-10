from flask import render_template
from flask.views import View

from src.library.plot import create_plot


class Index(View):

    def dispatch_request(self):
        feature = 'Bar'
        bar = create_plot(feature)
        return render_template('index.html', plot=bar)
