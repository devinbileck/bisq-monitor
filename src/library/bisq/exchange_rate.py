from datetime import datetime


class ExchangeRate(object):
    """Represents the spot price in Bitcoin for a given currency at a given time as reported by a given provider."""

    def __init__(self, currency, price, timestamp, provider):
        self.__currency = currency
        self.__price = price
        self.__timestamp = timestamp
        self.__provider = provider

    @property
    def currency(self):
        return self.__currency

    @property
    def price(self):
        return self.__price

    @property
    def timestamp(self):
        return self.__timestamp

    @property
    def provider(self):
        return self.__provider

    def __eq__(self, other):
        if isinstance(other, ExchangeRate) \
                and other.currency == self.currency \
                and other.price == self.price \
                and other.timestamp == self.timestamp \
                and other.provider == self.provider:
            return True
        return False

    def __repr__(self):
        return "<ExchangeRate {0}={1} @ {2} UTC from {3}>".format(
            self.currency, self.price,
            datetime.utcfromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S'), self.provider)

    def __str__(self):
        return "<ExchangeRate {0}={1} @ {2} UTC from {3}>".format(
            self.currency, self.price,
            datetime.utcfromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S'), self.provider)
