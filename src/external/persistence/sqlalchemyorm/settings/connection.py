"""_summary_
adapted by: https://github.com/programadorLhama/CleanArch/blob/master/src/infra/db/settings/connection.py
"""
import os
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine

DB_DIALECT  = os.getenv('DB_DIALECT')
DB_USER     = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST     = os.getenv('DB_HOST')
DB_PORT     = os.getenv('DB_PORT')
DB_DATABASE = os.getenv('DB_DATABASE')
DB_SCHEMA   = os.getenv('DB_SCHEMA')


class DBConnectionHandler:

    def __init__(self) -> None:
        self._connection_string = "{}://{}:{}@{}:{}/{}".format(
            DB_DIALECT,
            DB_USER,
            DB_PASSWORD,
            DB_HOST,
            DB_PORT,
            DB_DATABASE
        )
        self._engine = self._create_database_engine()
        self._get_section()

    def _create_database_engine(self):
        engine = create_engine(self._connection_string)
        return engine

    def get_engine(self):
        return self._engine 

    def _get_section(self):
        session_make = sessionmaker(bind=self._engine)
        self.session = session_make()

    def close(self):
        self.session.close()