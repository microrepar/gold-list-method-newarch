"""_summary_
adapted by: https://github.com/programadorLhama/CleanArch/blob/master/src/infra/db/settings/connection.py
"""
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine

from config import Config


class DBConnectionHandler:

    def __init__(self) -> None:
        self._connection_string = Config.DATABASE_URL
        self._session = None
        
    def _create_database_engine(self):
        engine = create_engine(self._connection_string)
        return engine

    def _get_section(self):
        self._engine = self._create_database_engine()
        session_make = sessionmaker(bind=self._engine)
        self._session = session_make()
    
    @property
    def session(self):
        if self._session:
            return self._session        
        
        self._get_section()
        return self._session
    
    def close(self):
        if self._session:
            self._session.close()
            self._session = None