from src.core import usecase_map
from src.core.shared.application import Result
from src.core.shared.usecase import UseCase
from src.core.user import User

from .user_repository import UserRepository


@usecase_map('/user/delete')
class UserLogicRemove(UseCase):

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def execute(self, entity: User) -> Result:
        result = Result()
        
        user_exists = self.repository.find_by_field(entity)
        
        if not user_exists:
            result.msg = f'Username={entity.username} no exists'
            result.entities = entity
            return result
        else:
            user_exists = user_exists[-1]
        
        user_exists.status = 'removed'
        
        try:
            updated_user = self.repository.update(user_exists)
            result.entities = updated_user
            return result
        except Exception as error:
            result.msg = str(error)
            result.entities = entity
            return result
