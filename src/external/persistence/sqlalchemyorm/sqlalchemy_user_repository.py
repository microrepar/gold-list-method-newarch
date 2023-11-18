from typing import List

from src.core.user import User, UserRepository
from src.external.persistence import repository_map

from .model.base import UserModel
from .settings.connection import DBConnectionHandler


@repository_map
class SlalchemyUserRepository(UserRepository):

    def __init__(self):
        self.database = DBConnectionHandler()
        pass
    
    def registry(self, entity: User) -> User:
        
        model = UserModel.user_entity_to_model(entity)
        try:
            with self.database.session.begin():
                self.database.session.add(model)
            
            new_entity = UserModel.user_model_to_entity(model)
            return new_entity
        
        except Exception as error:
            self.database.session.rollback()
            raise error
        finally:
            self.database.close()

    def get_all(self, entity: User) -> List[User]:
        
        try:
            model_list = self.database.session.query(UserModel).all()
            entity_list = [UserModel.user_model_to_entity(m) for m in model_list]

            return entity_list
        except:
            pass
        finally:
            self.database.close()
        
    def update(self, entity: User) -> User:
        
        try:
            with self.database.session.begin():
                model : UserModel = (self.database.session
                                     .query(UserModel)
                                     .filter_by(id=entity.id)
                                     .one_or_none())
                
                if model is None:
                    raise Exception(f'There is no User with id={entity.id}')
                
                model.name            = entity.name
                model.status          = entity.status
                model.age             = entity.age
                model.email           = entity.email
                model.username        = entity.username
                model.password        = entity.password
                model.repeat_password = entity.repeat_password
            
            updated_entity = UserModel.user_model_to_entity(model)
            return updated_entity
            
        except Exception as error:
            self.database.session.rollback()
            raise error
        finally:
            self.database.close()
    
    def find_by_field(self, entity: User) -> List[User]:
        
        filters = dict([v for v in vars(entity).items() if not v[0].startswith('_') and bool(v[-1])])

        kwargs = {}
        for attr, value in filters.items():
            if bool(value) is False: 
                continue                        
            elif attr in 'username email id':
                ...
            else:
                raise Exception(f'This field "{attr}" cannot be used to find Users!')
            
            kwargs[attr] = value
        
        try:
            with self.database.session.begin():
                    
                model_list =  self.database.session.query(UserModel).filter_by(**kwargs).all()

                entity_list = []
                for model in model_list:
                    entity_found = UserModel.user_model_to_entity(model)
                    entity_list.append(entity_found)
            
            return entity_list

        except Exception as error:
            self.database.session.rollback()
            raise error
        finally:
            self.database.close()

    
    def remove(self, entity: User) -> bool:        
        raise Exception('"remove" method in "SlalchemyUserRepository" is not implemented')
        # model = None
        # try:
        #     with self.database.session.begin():
        #         model = self.database.session.query(UserModel).filter_by(id=entity.id).firt()
        #         self.database.session.delete(model)
        # except Exception as error:
        #     self.database.session.rollback()
        #     return False
        # finally:
        #     self.database.close()



    def get_by_id(self, entity: User) -> User:
        raise Exception('"get_by_id" method in "SlalchemyUserRepository" is not implemented')