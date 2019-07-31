from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.model.base_model import Base


class Database(object):

    def __init__(self, db_name):
        engine_url = 'sqlite:///{DB}'.format(DB=db_name)
        self.engine = create_engine(engine_url)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()
