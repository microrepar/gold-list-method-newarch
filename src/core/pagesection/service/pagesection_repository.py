from abc import abstractmethod
from typing import List, Protocol, runtime_checkable

from ..model.pagesection import PageSection


@runtime_checkable
class PageSectionRepository(Protocol):

    @abstractmethod
    def registry(self, entity: PageSection) -> None :
        """Registry a PageSection into database 
        """

    @abstractmethod
    def get_all(self) -> List[PageSection]:
        """Get all registred PageSections in database
        """
