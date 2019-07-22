import logging

from requests import HTTPError

from src.library.bisq.exchange_rate import ExchangeRate
from src.library.bisq.fee_rate import FeeRate
from src.library.tor_session import IncorrectResponseData

log = logging.getLogger(__name__)


class PriceNode(object):
    """Represents a Bisq network price node."""

    def __init__(self, address):
        self.__address = address

    @property
    def address(self):
        return self.__address

    def is_online(self, tor_session):
        try:
            self.get_version(tor_session)
            return True
        except ConnectionError as e:
            log.debug(e)
        return False

    def get_version(self, tor_session):
        return tor_session.get_text_data("http://{}/getVersion".format(self.address))

    def get_current_fees(self, tor_session):
        fees = {}
        json_data = tor_session.get_json_data("http://{}/getFees".format(self.address))
        if 'dataMap' not in json_data:
            raise IncorrectResponseData("JSON content does not contain 'dataMap'")
        for key, value in json_data['dataMap'].items():
            if not key.endswith("TxFee"):
                raise IncorrectResponseData("Invalid content in JSON 'dataMap': {}".format(json_data['dataMap']))
            currency = key[:-5]     # strip "TxFee" to get the currency name
            fee_rate = FeeRate(currency, value, json_data['bitcoinFeesTs'])
            fees[currency] = fee_rate
        return fees

    def get_current_market_prices(self, tor_session):
        prices = {}
        json_data = tor_session.get_json_data("http://{}/getAllMarketPrices".format(self.address))
        if 'data' not in json_data:
            raise IncorrectResponseData("JSON content does not contain 'data'")
        for currency in json_data['data']:
            if any(x not in currency for x in ['currencyCode', 'price', 'timestampSec', 'provider']):
                raise IncorrectResponseData("Invalid content in JSON 'data': {}".format(json_data['data']))
            exchange_rate = ExchangeRate(currency['currencyCode'], currency['price'], currency['timestampSec']/1000, currency['provider'])
            prices[currency['currencyCode']] = exchange_rate
        return prices

    def __eq__(self, other):
        if isinstance(other, PriceNode) and other.address == self.address:
            return True
        return False

    def __repr__(self):
        return "<PriceNode {}>".format(self.address)

    def __str__(self):
        return "<PriceNode {}>".format(self.address)
