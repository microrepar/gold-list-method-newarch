
"""persistence module
"""

class RepositoryNotFoundError():
    def __init__(self):
        pass

 
repositories = {'default': RepositoryNotFoundError}


def repository_map(cls):
    repositories.update({cls.__base__.__name__: cls})
    return cls


from .sqlalchemyorm import sqlalchemy_notebook_repository, sqlalchemy_pagesection_repository, sqlalchemy_sentence_repository
