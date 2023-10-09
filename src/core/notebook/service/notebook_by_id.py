from typing import List

from ...shared import UseCase
from .. import Notebook, NotebookRepository
from ...shared.application import Result
from ... import usecase_map


@usecase_map('/notebook/id')
class NotebookGetById(UseCase):

    def __init__(self, *, repository: NotebookRepository):
        self.repository = repository

    def execute(self, notebook: Notebook) -> Result:
        result = Result()
        has_notebook = self.repository.get_by_id(notebook)

        if not has_notebook:
            result.msg = f'There are no registred notebooks!'
            result.entidades = notebook
            return result
        
        result.entidades = has_notebook
        return result
