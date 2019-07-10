from flask import Flask
from flask_restful import Api
from werkzeug.middleware.proxy_fix import ProxyFix

from src.api.chart import Chart
from src.views.index import Index


class WebApp(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.app.wsgi_app = ProxyFix(self.app.wsgi_app)

        api = Api(self.app)
        api.add_resource(Chart, '/chart')

        self.app.add_url_rule('/', view_func=Index.as_view('index'))

    def run(self):
        self.app.run(host=self.host, port=self.port)
