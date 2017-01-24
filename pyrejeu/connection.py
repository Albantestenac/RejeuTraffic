# -*- coding: utf-8 -*-

from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from models import Base


class DatabaseConnection(object):
    Session = scoped_session(sessionmaker())

    def __init__(self, file_path=None, **kwargs):
        if file_path is None:
            file_path = ":memory:"
            kwargs.update({
                "connect_args": {'check_same_thread': False},
                "poolclass": StaticPool
            })
        self.engine = create_engine('sqlite:///%s' % file_path,
                                    echo=False, **kwargs)
        # configure scoped session
        self.Session.configure(bind=self.engine)
        # create database
        Base.metadata.create_all(self.engine)

    def get_engine(self):
        return self.engine

    def get_session(self):
        return self.Session()
