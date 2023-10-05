"""Módulo contendo a classe DAO Abstrata e as classes concretas
"""

import abc
from typing import List


class AbstractDAO(abc.ABC):

    @abc.abstractmethod
    def insert(self, entity) -> 'entity':
        """Get a entity as a parameter to be inserted into database
        """        

    @abc.abstractmethod
    def get_all(self, entity) -> List['entity_list']:
        """Get entity as a parameter to be found all entities same types on database
        """

    @abc.abstractmethod
    def get_by_id(self, entity) -> 'entity':
        """Get entity as a parameter to be found by id on database
        """
    
    @abc.abstractmethod
    def update(self, entity) -> 'entity':
        """Get entity as a parameter to be updated
        """
        
    @abc.abstractmethod
    def find_by_field(self, entity) -> List['entity']:
        """Get entity as a parameter to be found by fields on database
        """

    @abc.abstractmethod
    def delete(self, entity) -> bool:
        """Get entity as a parameter to be removed by id on database
        """

########################### Classe Concreta - DAO de Base para implementar##################################
class _DAO(AbstractDAO):

    def insert(self, entity) -> 'entity':
        pass

    def get_all(self, entity) -> List['entity_list']:
        pass

    def get_by_id(self, entity) -> 'entity':
        pass

    def update(self, entity) -> bool:
        pass

    def find_by_field(self, entity) -> List['entity']:
        pass

    def delete(self, entity) -> bool:
        pass
########################### Classe Concreta - DAO de Base para implementar##################################
