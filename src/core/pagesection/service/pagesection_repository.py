from abc import abstractmethod
from typing import Protocol, runtime_checkable

from src.core.shared.application import Result

from ..model.pagesection import PageSection


@runtime_checkable
class PageSectionRepository(Protocol):

    @abstractmethod
    def registry(self, entity: PageSection) -> Result:
        """Registry a PageSection into database 
        """

    @abstractmethod
    def get_all(self, entity: PageSection = None) -> Result:
        """Get all registred PageSections in database
        """

    @abstractmethod
    def get_by_id(self, entity: PageSection) -> Result:
        """Get by id a registred PageSection in database
        """
    
    @abstractmethod
    def find_by_field(self, entity: PageSection) -> Result:
        """Get by id a registred PageSection in database
        """
    
    @abstractmethod
    def get_last_page_number(self, entity: PageSection) -> Result:
        """Get next page number to PageSection
        """
    
    @abstractmethod
    def update(self, entity: PageSection) -> Result:
        """Update page number in database
        """

    