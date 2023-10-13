import datetime
from ...shared.application import Result

from ...shared.usecase import UseCase
from ..model.pagesection import PageSection, Group
from .pagesection_repository import PageSectionRepository
from ....core import usecase_map


@usecase_map('/pagesection/update')
class PageSectionUpdate(UseCase):

    def __init__(self, repository: PageSectionRepository):
        
        self.repository = repository

    def execute(self, entity: PageSection) -> Result:
        result = Result()

        try:
            updated_pagesection = self.repository.update(entity)
            result.entidades = updated_pagesection
            return result
        
        except Exception as error:
            result.msg = str(error)
            result.entidades = entity
            return result        
        