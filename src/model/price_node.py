import json

from sqlalchemy import Column
from sqlalchemy.types import BigInteger, String

from src.library.configuration import Configuration

db = Configuration.database


class PriceNode(db.Model):
    __tablename__ = 'price_node'

    id = Column(BigInteger, primary_key=True)
    address = Column(String)
    operator = Column(String)

    def __init__(self, address, operator=""):
        self.address = address
        self.operator = operator

    def to_dict(self):
        return {"address": self.address, "operator": self.operator}

    @staticmethod
    def parse(**kwargs):
        address = kwargs.get('address', None)
        operator = kwargs.get('operator', None)
        return PriceNode.factory(address, operator)

    def __str__(self):
        return json.dumps(self.to_dict())

    def __repr__(self):
        return json.dumps(self.to_dict())

    def __eq__(self, other):
        if isinstance(other, PriceNode):
            return self.address == other.address
        return False

    @staticmethod
    def factory(address, operator=None):
        if operator:
            price_node = PriceNode.query.filter_by(address=address, operator=operator).first()
        else:
            price_node = PriceNode.query.filter_by(address=address).first()
        if price_node:
            return price_node
        else:
            return PriceNode(address, operator)
