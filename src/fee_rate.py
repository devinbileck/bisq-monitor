from datetime import datetime


class FeeRate(object):
    """Represents the mining fee rate for a given base currency."""

    def __init__(self, currency, price, timestamp):
        self.currency = currency
        self.price = price
        self.timestamp = timestamp

    def __eq__(self, other):
        if isinstance(other, FeeRate) \
                and other.currency == self.currency \
                and other.price == self.price \
                and other.timestamp == self.timestamp:
            return True
        return False

    def __repr__(self):
        return "<FeeRate {0}={1} @ {2} UTC>".format(
            self.currency, self.price, datetime.utcfromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S'))

    def __str__(self):
        return "<FeeRate {0}={1} @ {2} UTC>".format(
            self.currency, self.price, datetime.utcfromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S'))
