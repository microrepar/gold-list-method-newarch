from ...shared.application import Result

from ...shared.usecase import UseCase
from ..model.pagesection import PageSection
from .pagesection_repository import PageSectionRepository
from ....core import usecase_map


@usecase_map('/pagesection')
class PageSectionGetAll(UseCase):

    def __init__(self, repository: PageSectionRepository):
        self.repository = repository

    def execute(self, entity: PageSection=None) -> Result:
        result = Result()

        pagesection_list = self.repository.get_all()

        if len(pagesection_list) == 0:
            result.msg = f'There are no page sections into notebook.'
            return result
        
        result.entidades = pagesection_list
        
        return result