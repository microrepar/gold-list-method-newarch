from typing import List
from src.core.notebook import Notebook, NotebookRepository
import redis
import streamlit as st

class RedisNotebookRepository(NotebookRepository):

    def __init__(self):
        self.redis = redis.Redis(host=st.secrets.HOST,
                        port=st.secrets.PORT,
                        password=st.secrets.PASSWORD, 
                        decode_responses=True)     

    def registry(*, name: str, 
                 foreign_language: str, 
                 mother_idiom: str, 
                 list_size: int, 
                 days_period: int) -> None:
        
        return super().registry(name, foreign_language, 
                                mother_idiom, list_size, days_period)

    def get_all() -> List[Notebook]:
        pass