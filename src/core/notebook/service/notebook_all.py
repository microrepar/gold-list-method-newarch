from typing import List

from ...shared import UseCase
from .. import Notebook, NotebookRepository
from ...shared.application import Result
from ... import usecase_map


@usecase_map('/notebook')
class NotebookAllService(UseCase):

    def __init__(self, *, repository: NotebookRepository):
        self.repository = repository

    def execute(self, notebook: Notebook) -> Result:
        result = Result()
        notebook_list = self.repository.get_all()

        if not notebook_list:
            result.msg = f'There are no registred notebooks!'
            result.entidades = notebook_list
            return result
        
        result.entidades = notebook_list
        return result
