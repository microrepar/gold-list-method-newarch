import datetime
from typing import Generic

from src.core import usecase_map
from src.core.shared.application import Result

from ...notebook import Notebook
from ...shared.application import Result
from ...shared.usecase import UseCase
from ..model.pagesection import Group, PageSection
from .pagesection_repository import PageSectionRepository


@usecase_map('/pagesection')
class PageSectionFindByField(UseCase):

    def __init__(self, repository: PageSectionRepository):
        self.repository = repository

    def execute(self, entity: PageSection) -> Result:
        return super().execute(entity)