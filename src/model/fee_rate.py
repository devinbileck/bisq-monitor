import datetime
import json

from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import BigInteger, String, DateTime

from src.library.bisq.price_node import PriceNode
from src.library.server_cache import ServerCache

db = ServerCache.database


class FeeRate(db.Model):
    __tablename__ = 'fee_rate'

    id = Column(BigInteger, primary_key=True)
    price_node_id = Column(BigInteger, ForeignKey('price_node.id'), nullable=False)
    currency = Column(String, nullable=False)
    price = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=False), nullable=False)

    price_node = db.relationship('PriceNode')

    def __init__(self, price_node, currency, price, timestamp):
        if not isinstance(price_node, PriceNode):
            raise TypeError("'price_node' in fee_rate must be an instance of PriceNode")
        if not isinstance(timestamp, datetime.datetime):
            raise TypeError("'timestamp' in fee_rate must be an instance of datetime")
        self.price_node = price_node
        self.currency = currency
        self.price = price
        self.timestamp = timestamp

    def to_dict(self):
        return {"price_node": self.price_node,
                "currency": self.currency,
                "price": self.price,
                "timestamp": self.timestamp}

    @staticmethod
    def parse(**kwargs):
        return FeeRate(kwargs['price_node'],
                       kwargs['currency'],
                       kwargs['price'],
                       kwargs['timestamp'])

    def __str__(self):
        return json.dumps(self.to_dict())

    def __repr__(self):
        return json.dumps(self.to_dict())

    def __eq__(self, other):
        if isinstance(other, FeeRate):
            if self.price_node == other.price_node and \
                    self.currency == other.currency and \
                    self.price == other.price and \
                    self.timestamp == other.timestamp:
                return True
        return False
