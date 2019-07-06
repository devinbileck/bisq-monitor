import requests
from requests import HTTPError


class TorSession(object):

    def __init__(self, socks_host='127.0.0.1', socks_port=9050):
        self.session = requests.session()
        self._socks_host = socks_host
        self._socks_port = socks_port
        self.update_proxies()

    @property
    def socks_host(self):
        return self._socks_host

    @socks_host.setter
    def socks_host(self, value):
        self._socks_host = value
        self.update_proxies()

    @property
    def socks_port(self):
        return self._socks_port

    @socks_port.setter
    def socks_port(self, value):
        if value < 0 or value > 65535:
            raise ValueError("Port out of range")
        self._socks_port = value
        self.update_proxies()

    def update_proxies(self):
        self.session.proxies = {
            "http": "socks5h://{0}:{1}".format(self._socks_host, self._socks_port),
            "https": "socks5h://{0}:{1}".format(self._socks_host, self._socks_port)
        }

    def get_response(self, url):
        response = self.session.get(url)
        if response.status_code != 200:
            raise HTTPError("{0} returned HTTP error {1}".format(url, response.status_code))
        return response

    def get_text_data(self, url):
        response = self.get_response(url)
        return response.text

    def get_json_data(self, url):
        response = self.get_response(url)
        try:
            json_data = response.json()
        except ValueError:
            raise IncorrectResponseData("Response not in JSON format: {}".format(response))
        return json_data


class IncorrectResponseData(Exception):
    """Raised when the response data is not as expected."""
    pass
