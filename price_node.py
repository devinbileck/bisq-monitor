from exchange_rate import ExchangeRate
from fee_rate import FeeRate
from tor_session import IncorrectResponseData


class PriceNode(object):

    def __init__(self, address):
        self.address = address

    def get_fees(self, tor_session):
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

    def get_all_market_prices(self, tor_session):
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

    def get_version(self, tor_session):
        return tor_session.get_text_data("http://{}/getVersion".format(self.address))

    def __repr__(self):
        return "<PriceNode {}>".format(self.address)

    def __str__(self):
        return "<PriceNode {}>".format(self.address)
