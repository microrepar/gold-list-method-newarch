from abc import abstractmethod
from typing import List, Protocol, runtime_checkable

from ..model.notebook import Notebook


@runtime_checkable
class NotebookRepository(Protocol):

    @abstractmethod
    def registry(self, entity: Notebook) -> None :
        """Registry a notebook into database
        """

    @abstractmethod
    def get_all(self, entity: Notebook = None) -> List[Notebook]:
        """Get all registred notebooks in database
        """
    
    @abstractmethod
    def get_by_id(self, entity: Notebook) -> Notebook:
        """Get by id registred notebooks in database
        """
    
    @abstractmethod
    def find_by_field(self, entity: Notebook) -> List[Notebook]:
        """Find by id registred notebooks in database
        """
