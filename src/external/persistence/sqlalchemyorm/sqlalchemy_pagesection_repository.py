import datetime
from typing import List

from sqlalchemy import and_, func

from src.core.pagesection import PageSection, PageSectionRepository, Group
from src.core.notebook import Notebook
from src.core.sentence import Sentence

from ...persistence import repository_map
from .model.base import NotebookModel, PageSectionModel, SentenceModel, pagesection_sentence_assoc
from .settings.connection import DBConnectionHandler


@repository_map
class SqlAlchemyPageSectionRepository(PageSectionRepository):
    """SqlAlchemy implementation of PageSectionRepository"""

    def __init__(self):
        self.database = DBConnectionHandler()

    def get_all(self) -> List[PageSection]:
        try:
            instance_page_list = self.database.session.query(PageSectionModel).all()
            
            entity_page_list = []
                            
            for instance_page in instance_page_list:
                entity: PageSection = None 
                entity = PageSectionModel.pagesection_model_to_entity(instance_page)
                entity.sentences = list()            

                instance_sentence_list = instance_page.sentences
                for instance_sentence in instance_sentence_list:
                    entity_sentence: Sentence = None
                    entity_sentence = SentenceModel.sentence_model_to_entity(instance_sentence)    
                    entity.sentences.append(entity_sentence)
            
                entity_page_list.append(entity)
            return entity_page_list
        
        except Exception as error:
            self.database.session.rollback()
            raise error
        finally:
            self.database.close()


    def get_by_id(self, entity: PageSection) -> PageSection:
        
        try:
            with self.database.session.begin():
                instance = self.database.session.query(PageSectionModel).filter(
                    and_(
                        PageSectionModel.created_at == entity.created_at, 
                        PageSectionModel.distillation_at == entity.created_at,
                        PageSectionModel.group == entity.group.value
                    )
                ).one_or_none()

                if instance:
                    return PageSectionModel.pagesection_model_to_entity(instance)            
                return
                
        except Exception as error:
            self.database.session.rollback()
            return str(error)


    def find_by_field(self, entity: PageSection) -> List[PageSection]:

        filters = dict([v for v in vars(entity).items() if not v[0].startswith('_') and bool(v[-1])])

        kwargs = {}
        for attr, value in filters.items():
            if bool(value) is False: continue

            if isinstance(value, Notebook):
                attr = 'notebook_id'
                value = int(value.id)
            elif isinstance(value, Group):
                attr = '_group'
                value = value.value            
            elif isinstance(value, PageSection):
                attr = 'created_by_id'
                value = value.created_by.id
            elif attr in 'created_at':
                if isinstance(value, datetime.date):
                    value = value
                    # value = pd.to_datetime(value).strftime("%Y-%m-%d")
                elif '#' in value:
                    value = None
            elif attr in 'section_number distillated distillation_at':
                ...
            else:
                raise Exception(f'This field "{attr}" cannot be used to find PageSection objects!')
            
            kwargs[attr] = value

        try:
            with self.database.session.begin():
                    
                instance_page_list = self.database.session.query(PageSectionModel).filter_by(**kwargs).all()

                entity_page_list = []
                        
                for instance_page in instance_page_list:
                    entity: PageSection = None 
                    entity = PageSectionModel.pagesection_model_to_entity(instance_page)
                    entity.sentences = list()            

                    instance_sentence_list = instance_page.sentences
                    for instance_sentence in instance_sentence_list:
                        entity_sentence: Sentence = None
                        entity_sentence = SentenceModel.sentence_model_to_entity(instance_sentence)    
                        entity.sentences.append(entity_sentence)
                
                    entity_page_list.append(entity)

                return entity_page_list

        except Exception as error:
            self.database.session.rollback()
            raise error

    def get_last_page_number(self, entity: PageSection=None) -> int:
        try:
            with self.database.session.begin():

                instance: PageSectionModel = PageSectionModel.pagesection_entity_to_model(entity)

                instance.notebook = None
                instance.sentences = list()

                if instance.page_number is None:
                    next_page_number = (self.database.session.query(func.max(PageSectionModel.page_number))
                                    .filter(PageSectionModel.notebook_id == entity.notebook.id)
                                ).scalar()
                    next_page_number = next_page_number + 1 if next_page_number is not None else 1
                    instance.page_number = next_page_number
                
            return next_page_number
            
        except Exception as error:
            self.database.session.rollback()
            raise error

    def update(self, entity: PageSection) -> PageSection:
        try:
            with self.database.session.begin():
                instance: PageSectionModel = (self.database.session
                                              .query(PageSectionModel)
                                              .filter_by(id=entity.id)
                                              .one_or_none())
                if instance is None:
                    raise Exception(f'There is no PageSection with id={entity.id}')
                
                if entity.created_by is not None:
                    instance.created_by_id = entity.created_by.id
                    inner_page_entity = (self.database.session
                                         .query(PageSectionModel)
                                         .filter_by(id=entity.created_by.id)
                                         .one_or_none())

                instance.distillated          = entity.distillated
                instance.distillation_actual  = entity._distillation_actual
                instance.memorializeds        = entity.memorializeds
                instance.translated_sentences = entity.translated_sentences
                
                for index, sentence in enumerate(instance.sentences):
                    self.database.session.query(pagesection_sentence_assoc).filter(
                        pagesection_sentence_assoc.c.pagesection_id == instance.id,
                        pagesection_sentence_assoc.c.sentence_id == sentence.id
                    ).update({'memorialized': entity.memorializeds[index],
                              'distillated': entity.distillated,})

            updated_entity = PageSectionModel.pagesection_model_to_entity(instance)
            updated_entity.notebook = NotebookModel.notebook_model_to_entity(instance.notebook)
            updated_entity.sentences = [SentenceModel.sentence_model_to_entity(s) for s in instance.sentences]
            
            if entity.created_by is not None:
                updated_entity.created_by = PageSectionModel.pagesection_model_to_entity(inner_page_entity)

            return updated_entity

        except Exception as error:
            self.database.session.rollback()
            raise error
        finally:
            del entity
            self.database.close()

    def get_sentences_by_group(self, entity: PageSection):
        try:
            results = None
            with self.database.session.begin():
                sentences_id = (self.database.session.query(pagesection_sentence_assoc.c.sentence_id)
                                .filter(pagesection_sentence_assoc.c.group == entity.group.value)
                                .all())

                id_list = [s.sentence_id for s in sentences_id]

                results = (self.database.session.query(SentenceModel)
                           .filter(SentenceModel.id.in_(id_list))
                           .all())
            
            sentence_list = [SentenceModel.sentence_model_to_entity(m) for m in results]

            return sentence_list

        except Exception as error:            
            self.database.session.rollback()
            raise error

    def registry(self, entity: PageSection) -> PageSection:
        try:
            instance = None
            with self.database.session.begin():

                has_notebook: NotebookModel = (self.database.session
                                               .query(NotebookModel)
                                               .filter_by(id=entity.notebook.id)
                                               .one_or_none())
                if not has_notebook:
                    self.database.session.rollback()
                    raise Exception(f'Notebook id={entity.notebook.id} was not found.' )
                
                instance: PageSectionModel = PageSectionModel.pagesection_entity_to_model(entity)

                instance.notebook = None
                instance.sentences = list()

                for sentence in entity.sentences:
                    has_sentence = (self.database.session.query(SentenceModel)
                                    .filter_by(foreign_language=sentence.foreign_language)
                                    .first())
                    if has_sentence:
                        is_memorialized_sentence = self.database.session.query(pagesection_sentence_assoc).filter(
                            pagesection_sentence_assoc.c.sentence_id == has_sentence.id,
                            pagesection_sentence_assoc.c.memorialized == True,
                            pagesection_sentence_assoc.c.notebook_id == has_notebook.id
                        ).first()
                        
                        exists_sentence_in_headlist = self.database.session.query(pagesection_sentence_assoc).filter(
                            pagesection_sentence_assoc.c.sentence_id == has_sentence.id,
                            pagesection_sentence_assoc.c.group == Group.A.value,
                            pagesection_sentence_assoc.c.distillated == False,
                            pagesection_sentence_assoc.c.notebook_id == has_notebook.id
                        ).first()

                        if is_memorialized_sentence:                            
                            raise Exception(f'This Sentece: "{has_sentence.foreign_language}" '
                                            f'was already memorialized in page={is_memorialized_sentence.page} '
                                            f'and group={is_memorialized_sentence.group}.')
                        if exists_sentence_in_headlist:
                            raise Exception(f'This Sentece: "{has_sentence.foreign_language}" '
                                            f'already exists in page={exists_sentence_in_headlist.page} '
                                            f'and group={exists_sentence_in_headlist.group}.')
                        else:
                            instance.sentences.append(has_sentence)

                            self.database.session.query(pagesection_sentence_assoc).filter(
                                pagesection_sentence_assoc.c.sentence_id == has_sentence.id,
                                pagesection_sentence_assoc.c.group == Group.NEW_PAGE.value
                            ).update({'group': Group.REMOVED.value, 'distillated': True})


                    else:
                        instance.sentences.append(
                            SentenceModel.sentence_entity_to_model(sentence)
                        )
                
                instance.notebook_id = has_notebook.id
                has_notebook.page_section_list.append(instance)
                self.database.session.add(instance)

                group_value = instance._group
                for sentence in instance.sentences:
                    self.database.session.query(pagesection_sentence_assoc).filter(
                        pagesection_sentence_assoc.c.pagesection_id == instance.id,
                        pagesection_sentence_assoc.c.sentence_id == sentence.id
                    ).update({'group': group_value,
                              'page': instance.page_number,
                              'notebook_id': instance.notebook_id,
                              'distillated': instance.distillated,})

            new_entity = PageSectionModel.pagesection_model_to_entity(instance)
            new_entity.notebook = NotebookModel.notebook_model_to_entity(has_notebook)
            new_entity.sentences = [SentenceModel.sentence_model_to_entity(s) for s in instance.sentences]

            return new_entity
            
        except Exception as error:
            self.database.session.rollback()
            raise error
        finally:
            del entity
            self.database.close()
