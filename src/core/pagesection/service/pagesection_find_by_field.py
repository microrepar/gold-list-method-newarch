import datetime
from typing import Generic

from core.shared.application import Result

from ....core import usecase_map
from ...notebook import Notebook
from ...shared.application import Result
from ...shared.usecase import UseCase
from ..model.pagesection import PageSection, Group
from .pagesection_repository import PageSectionRepository


@usecase_map('/pagesection')
class PageSectionFindByField(UseCase):

    def __init__(self, repository: PageSectionRepository):
        self.repository = repository

    def execute(self, entity: PageSection -> Result:
        return super().execute(entity)