import datetime

from src.core.shared.entity import Entity
from src.core.shared.utils import date_to_string


class Sentence(Entity):
    def __init__(self, *,
                 id_              : int=None,
                 created_at       : datetime.date=None,
                 foreign_language : str=None,
                 mother_tongue    : str=None,
                 foreign_idiom    : str=None,
                 mother_idiom     : str=None
                 ):
        self.id               = id_
        self.created_at       = created_at
        self.foreign_idiom    = foreign_idiom
        self.mother_idiom     = mother_idiom
        self._foreign_language = None
        self._mother_tongue = None

        self.foreign_language = foreign_language
        self.mother_tongue = mother_tongue

    @property
    def foreign_language(self):
        return self._foreign_language
    
    @foreign_language.setter
    def foreign_language(self, value):
        if value:
            value = value.strip().split()
            self._foreign_language = ' '.join(value)
        
    @property
    def mother_tongue(self):
        return self._mother_tongue
    
    @mother_tongue.setter
    def mother_tongue(self, value):
        if value:
            value = value.strip().split()
            self._mother_tongue = ' '.join(value)
    
    def data_to_dataframe(self):
        return [
            {
                'id'               : self.id,
                'created_at'       : self.created_at,
                'foreign_language' : self.foreign_language,
                'mother_tongue'    : self.mother_tongue,
                'foreign_idiom'    : self.foreign_idiom,
                'mother_idiom'     : self.mother_idiom,
            }
        ]
    
    def data_to_redis(self):
        return{
                'id'               : self.id,
                'created_at'       : date_to_string(self.created_at),
                'foreign_language' : self.foreign_language,
                'mother_tongue'    : self.mother_tongue,
                'foreign_idiom'    : self.foreign_idiom,
                'mother_idiom'     : self.mother_idiom,
            }
    
    def __str__(self):
        return (
            f'Sentence('
                f'id_={self.id}, '
                f'created_at={self.created_at}, '
                f'foreign_language={self.foreign_language}, '
                f'mother_tongue={self.mother_tongue} '
            f')'
        )
    
    def validate_data(self):
        messages = []

        if not self.foreign_language:
            return 'There are empty fiels.'