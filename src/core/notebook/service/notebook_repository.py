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
    def get_all(self) -> List[Notebook]:
        """Get all registred notebooks in database
        """
