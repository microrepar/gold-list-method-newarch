from ...shared.usecase import UseCase
from ..model.notebook import Notebook
from .notebook_repository import NotebookRepository


class NotebookRemove(UseCase):

    def __init__(self, *, repository: NotebookRepository):
        self.repository = repository

    def execute(self, notebook: Notebook) -> int:
        """return super().execute(notebook)"""