import json

from sqlalchemy import Column
from sqlalchemy.types import Integer, String

from src.model.base_model import Base


class PriceNodeModel(Base):
    __tablename__ = 'price_node'

    address = Column(String, primary_key=True)
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
        return PriceNodeModel.factory(address, operator)

    def __str__(self):
        return json.dumps(self.to_dict())

    def __repr__(self):
        return json.dumps(self.to_dict())

    def __eq__(self, other):
        if isinstance(other, PriceNodeModel):
            return self.address == other.address
        return False

    @staticmethod
    def factory(address, operator=None):
        if operator:
            price_node = PriceNodeModel.query.filter_by(address=address, operator=operator).first()
        else:
            price_node = PriceNodeModel.query.filter_by(address=address).first()
        if price_node:
            return price_node
        else:
            return PriceNodeModel(address, operator)
