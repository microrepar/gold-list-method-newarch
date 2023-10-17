from abc import abstractmethod
from typing import List, Protocol, runtime_checkable

from src.core.shared.repository import Repository

from ..model.pagesection import PageSection


@runtime_checkable
class PageSectionRepository(Repository, Protocol):

    @abstractmethod
    def registry(self, entity: PageSection) -> PageSection:
        """Registry a PageSection into database 
        """

    @abstractmethod
    def get_all(self, entity: PageSection = None) -> List[PageSection]:
        """Get all registred PageSections in database
        """

    @abstractmethod
    def get_by_id(self, entity: PageSection) -> PageSection:
        """Get by id a registred PageSection in database
        """
    
    @abstractmethod
    def find_by_field(self, entity: PageSection) -> List[PageSection]:
        """Get by id a registred PageSection in database
        """
    
    @abstractmethod
    def get_last_page_number(self, entity: PageSection) -> int:
        """Get next page number to PageSection
        """
    
    @abstractmethod
    def update(self, entity: PageSection) -> PageSection:
        """Update page number in database
        """

    