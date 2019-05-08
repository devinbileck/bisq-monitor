from datetime import datetime


class ExchangeRate(object):
    """Represents the spot price in Bitcoin for a given currency at a given time as reported by a given provider."""

    def __init__(self, currency, price, timestamp, provider):
        self.currency = currency
        self.price = price
        self.timestamp = timestamp
        self.provider = provider

    def __repr__(self):
        return "<ExchangeRate {0}={1} @ {2} UTC from {3}>".format(
            self.currency, self.price,
            datetime.utcfromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S'), self.provider)

    def __str__(self):
        return "<ExchangeRate {0}={1} @ {2} UTC from {3}>".format(
            self.currency, self.price,
            datetime.utcfromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S'), self.provider)
