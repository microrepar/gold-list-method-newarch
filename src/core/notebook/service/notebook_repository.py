from abc import abstractmethod
from typing import Protocol, runtime_checkable

from src.core.shared.application import Result

from ..model.notebook import Notebook


@runtime_checkable
class NotebookRepository(Protocol):

    @abstractmethod
    def registry(self, entity: Notebook) -> Result :
        """Registry a notebook into database
        """

    @abstractmethod
    def get_all(self, entity: Notebook = None) -> Result:
        """Get all registred notebooks in database
        """
    
    @abstractmethod
    def get_by_id(self, entity: Notebook) -> Result:
        """Get by id registred notebooks in database
        """
    
    @abstractmethod
    def find_by_field(self, entity: Notebook) -> Result:
        """Find by id registred notebooks in database
        """
