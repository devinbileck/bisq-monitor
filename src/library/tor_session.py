import logging

import requests
from requests import HTTPError

log = logging.getLogger(__name__)


class TorSession(object):
    """Represents a session for communicating on the TOR network."""

    def __init__(self, socks5_host='127.0.0.1', socks5_port=9050):
        self.__session = requests.session()
        self.__socks5_host = socks5_host
        self.__socks5_port = socks5_port
        self.update_proxies()

    @property
    def socks5_host(self):
        return self.__socks5_host

    @socks5_host.setter
    def socks5_host(self, value):
        self.__socks5_host = value
        self.update_proxies()

    @property
    def socks5_port(self):
        return self.__socks5_port

    @socks5_port.setter
    def socks5_port(self, value):
        if value < 0 or value > 65535:
            raise ValueError("Port out of range")
        self.__socks5_port = value
        self.update_proxies()

    def update_proxies(self):
        self.__session.proxies = {
            "http": "socks5h://{0}:{1}".format(self.__socks5_host, self.__socks5_port),
            "https": "socks5h://{0}:{1}".format(self.__socks5_host, self.__socks5_port)
        }

    def get_response(self, url):
        try:
            response = self.__session.get(url)
        except Exception as ex:
            raise ConnectionError(ex)
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
