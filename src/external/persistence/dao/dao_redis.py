import datetime
import hashlib
import json
import os.path
from typing import List

import pandas as pd
import redis
import streamlit as st

from src.core.dao import AbstractDAO
from src.model import Group, Notebook, PageSection, Sentence

# The directory containing this file
HERE = os.path.abspath(os.path.dirname(__file__))


class NotebookDAO(AbstractDAO):
    def __init__(self):
        # connect to redis
        self.r = redis.Redis(host=st.secrets.HOST,
                        port=st.secrets.PORT,
                        password=st.secrets.PASSWORD, 
                        decode_responses=True)     


    def insert(self, entity: Notebook) -> Notebook:
        hash_main = entity.__class__.__name__

        # Get a id sequence to notebook
        entity.id = self.get_notebook_id_sequence()

        notebook_dict = entity.data_to_redis()

        new_notebook = json.dumps(notebook_dict)
        
        # Register the new notebook in redis
        is_inserted = self.r.hsetnx(hash_main, entity.name, new_notebook)

        # Checks if a notebook was inserted        
        if not is_inserted:
            raise Exception(f'Notebook name "{entity.name}" already exists. Choice another name to notebook!')
        
        self.set_map_id_name(entity)

        return entity


    def get_all(self, entity: Notebook) -> List[Notebook]:
        
        resp = self.r.hgetall(entity.__class__.__name__)
        
        notebook_list = list()
        
        for name, value in resp.items():
        
            data = json.loads(value)
        
            notebook_list.append(
                Notebook(
                    id_= data['id'],
                    name=data['name'],
                    created_at=data['created_at'],
                    updated_at=data['updated_at'],
                    list_size=data['list_size'],
                    days_period=data['days_period'],
                    foreign_idiom=data['foreign_idiom'],
                    mother_idiom=data['mother_idiom']
                )
            )

        return list(sorted(notebook_list, key=lambda x: x.id))


    def get_by_id(self, entity: Notebook) -> Notebook:
        hash_main_notebook_id = f'{entity.__class__.__name__}_id'
        hash_main_notebook = entity.__class__.__name__

        hash_key_name = self.r.hget(hash_main_notebook_id, entity.id)
        resp = self.r.hget(hash_main_notebook, hash_key_name)

        if not (hash_key_name and resp):
            raise Exception(f'There is no a notebook with id={entity.id}!')

        data = json.loads(resp)

        notebook = Notebook()

        notebook.id = data['id']
        notebook.name = data['name']
        notebook.created_at = data['created_at']
        notebook.updated_at = data['updated_at']
        notebook.list_size = data['list_size']
        notebook.days_period = data['days_period']
        notebook.foreign_idiom = data['foreign_idiom']
        notebook.mother_idiom = data['mother_idiom']

        hash_key_page_id_list = f'{notebook.__class__.__name__}_{notebook.id}'

        has_list = self.r.hget('notebook_has_page_section_id', hash_key_page_id_list)
        
        if has_list is None:
            notebook.page_section_list = list()
            return notebook

        data_list = json.loads(has_list)

        page_section_dao = PageSectionDAO()
        page_section_list = []
        for page_section_id in data_list:
            ps = page_section_dao.get_by_id(PageSection(id_=page_section_id))
            if ps:
                page_section_list.append(ps)

        notebook.page_section_list = page_section_list
            
        return notebook


    def update(self, entity: Notebook) -> Notebook:
        pass


    def find_by_field(self, entity: Notebook) -> List[Notebook]:
        pass


    def delete(self, entity: Notebook) -> bool:
        hash_main = entity.__class__.__name__
        
        hash_key = entity.name

        is_deleted = self.r.hdel(hash_main, hash_key)

        return is_deleted
  

    def set_map_id_name(self, entity):
        hash_main = f'{entity.__class__.__name__}_id'
        self.r.hsetnx(hash_main, entity.id, entity.name)


    def get_notebook_id_sequence(self):
        key_sequence = 'notebook_id_sequence'        
        if not self.r.exists(key_sequence):
            self.r.set(key_sequence, 0)
        new_id = self.r.incr(key_sequence)
        return new_id



class PageSectionDAO(AbstractDAO):
    def __init__(self):
        # connect to redis
        self.r = redis.Redis(host=st.secrets.HOST,
                        port=st.secrets.PORT,
                        password=st.secrets.PASSWORD, 
                        decode_responses=True)     
        

    def insert(self, entity: PageSection) -> PageSection:
        hash_main = entity.__class__.__name__

        
        page_section = PageSection()
        # Get a id sequence to notebook
        page_section.id = self.get_hash_checksum(entity)
        page_section.page_number = self.get_page_number(entity)
        page_section.section_number = self.get_section_number(entity)
        page_section.created_by = entity.created_by        
        page_section.group = entity.group
        page_section.created_at = entity.created_at
        page_section.distillation_at = entity.distillation_at
        page_section.distillated = entity.distillated
        page_section.sentences = entity.sentences
        page_section.translated_sentences = entity.translated_sentences
        page_section.memorializeds = entity.memorializeds
        page_section.notebook = entity.notebook

        page_section_dict = page_section.data_to_redis()

        new_page_section = json.dumps(page_section_dict)
        
        is_inserted = None
        if page_section.created_at:
            # Register the new notebook in redis
            is_inserted = self.r.hsetnx(hash_main, page_section.id, new_page_section)

        # Checks if a notebook was inserted        
        if not is_inserted:
            raise Exception(f'There is already a page for the group {page_section.group.value} and selected day {entity.created_at}!')
            
        self.set_map_id_notebook_to_id_page_section(page_section)
        self.set_map_page_number(entity)
        self.set_map_section_number(entity)

        return page_section
    

    def get_all(self, entity: PageSection) -> List[PageSection]:
        pass


    def get_by_id(self, entity: PageSection) -> PageSection:
        hash_main = entity.__class__.__name__
        hash_key_id = entity.id

        has_page_section = self.r.hget(hash_main, hash_key_id)
        
        if not has_page_section:
            return None

        data = json.loads(has_page_section)

        page_section = PageSection(
                id_                  = data['id'],
                section_number       = data['section_number'],
                created_at           = data['created_at'],
                group                = Group(data['group']),
                distillation_at      = data['distillation_at'],
                distillation_actual  = data['distillation_actual'],
                distillated          = data['distillated'],
                memorializeds        = data['memorized'],
                translated_sentences = data['translated_sentence']
            )

        sentences_id_list = data.get('sentences_id')

        if sentences_id_list is None:
            page_section.sentences = list()
            return page_section
        
        sentence_dao = SentenceDAO()
        sentence_list = []
        for sentence_id in sentences_id_list:
            sc = sentence_dao.get_by_id(Sentence(id_=sentence_id))
            if sc is not None:
                sentence_list.append(sc)
        
        page_section.sentences = sentence_list

        return page_section

        


    def update(self, entity: PageSection) -> PageSection:
        df = pd.read_parquet(page_section_file)

        df_page = df[df['section_number'] == entity.section_number]

        is_distillated = df_page['distillated'].tolist()[-1]

        if is_distillated:
            raise Exception(f'Changing PageSection "group {entity.group.value}" is not allowed because it has already been distilled.')

        id_list = df_page['id'].tolist()
        entity.set_id(min(id_list))

        df.drop(df[df['section_number'] == entity.section_number].index, inplace=True)

        # Registry new page_section into dataframe using pd.concat method 
        df_registro = pd.DataFrame(entity.data_to_dataframe())
        df_concat = pd.concat([df, df_registro], ignore_index=True)

        df_concat.to_parquet(page_section_file)

        return entity


    def find_by_field(self, entity: PageSection) -> List[PageSection]:
        df = pd.read_parquet(page_section_file)
        df_result = df.copy()

        notebook_dao = NotebookDAO()
        sentence_dao = SentenceDAO()

        pages = df_result['section_number'].unique().tolist()
        
        filters = dict([v for v in vars(entity).items() if not v[0].startswith('_') and bool(v[-1])])
        for attr, value in filters.items():
            if bool(value) is False: continue

            if isinstance(value, Notebook):
                attr = 'notebook_id'
                value = int(value.id)
            elif isinstance(value, Group):
                value = value.value            
            elif isinstance(value, PageSection):
                attr = 'created_by_id'
                value = value.created_by.section_number
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
            
            df_result = df_result[df_result[attr] == value]

        if df_result.empty:
            return []        
        
        result_list = list()

        pages = df_result['section_number'].unique().tolist()

        for page in pages:
            sentence_id_list         = []
            translated_sentence_list = []
            memorized_list           = []
            id_list                  = []

            df_page = df_result[df['section_number'] == page]
            for index, row in df_page.iterrows():
                id_list.append(row['id'])
                sentence_id_list.append(row['sentence_id'])
                translated_sentence_list.append(row['translated_sentence'])
                memorized_list.append(row['memorized'])
            else:
                sentences = []
                for id_ in sentence_id_list:
                    sentences.append(
                        sentence_dao.get_by_id(
                            Sentence(id_=id_)
                        )
                    )

                notebook = notebook_dao.get_by_id(
                    Notebook(id_=row['notebook_id'])
                )

                created_by = self.get_by_id(
                    PageSection(section_number=row['created_by_id'])
                )

                page_section = PageSection(
                    id_                  = min(id_list),
                    section_number          = row['section_number'],
                    created_at           = row['created_at'],
                    created_by           = created_by,
                    group                = Group(row['group']),
                    distillation_at      = row['distillation_at'],
                    distillation_actual  = row['distillation_actual'],
                    distillated          = row['distillated'],
                    memorializeds        = memorized_list,
                    translated_sentences = translated_sentence_list,
                    sentences            = sentences,
                    notebook             = notebook
                )

                result_list.append(page_section)

        return list(result_list)
    

    def delete(self, entity: PageSection) -> bool:
        pass


    def get_section_number(self, entity: PageSection):
        key_sequence = f'sec_num_id_nb{entity.notebook.id}_sequence'        
        if not self.r.exists(key_sequence):
            self.r.set(key_sequence, 1)
        new_id = self.r.get(key_sequence)
        return new_id
    

    def set_map_section_number(self, entity: PageSection):
        key_sequence = f'sec_num_id_nb{entity.notebook.id}_sequence'        
        if not self.r.exists(key_sequence):
            self.r.set(key_sequence, 0)
        self.r.incr(key_sequence)        

    
    def get_page_number(self, entity: PageSection):
        if entity.page_number is not None:
            return
        if entity.created_at:
            key_sequence = f'pg_num_nb{entity.notebook.id}_gp{entity.group.value}_sequence'
            if not self.r.exists(key_sequence):
                self.r.set(key_sequence, 1)
            new_page = self.r.get(key_sequence)
            return new_page
    

    def set_map_page_number(self, entity: PageSection):
        if entity.page_number is not None:
            return entity.page_number
        key_sequence = f'pg_num_nb{entity.notebook.id}_gp{entity.group.value}_sequence'
        if not self.r.exists(key_sequence):
            self.r.set(key_sequence, 0)
        self.r.incr(key_sequence)        

    
    def set_map_id_notebook_to_id_page_section(self, entity: PageSection):
        hash_main = f'notebook_has_page_section_id'
        hash_key = f"{entity.notebook.__class__.__name__}_{entity.notebook.id}"
        page_section_id = entity.id

        has_list = self.r.hget(hash_main, hash_key)

        if has_list is None:
            new_list = [page_section_id]
        else:
            has_list = has_list
            new_list = json.loads(has_list)
            new_list.append(page_section_id)
        
        list_json = json.dumps(new_list)
        resp = self.r.hset(hash_main, hash_key, list_json)
    
    
    def get_hash_checksum(self, entity: PageSection):
        
        text = f'{entity.created_at}{entity.distillation_at}{entity.page_number}{entity.group}{entity.notebook.id}'

        hash_obj = hashlib.sha256()
        hash_obj.update(text.encode('utf-8'))

        checksum = hash_obj.hexdigest()
        return checksum



class SentenceDAO(AbstractDAO):
    def __init__(self):
        # connect to redis
        self.r = redis.Redis(host=st.secrets.HOST,
                        port=st.secrets.PORT,
                        password=st.secrets.PASSWORD, 
                        decode_responses=True)
        

    def insert(self, entity: Sentence) -> Sentence:
        hash_main = entity.__class__.__name__

        # Get a id sequence to notebook
        entity.id = self.get_sentence_id_sequence()

        sentence_dict = entity.data_to_redis()

        new_sentence = json.dumps(sentence_dict)
        
        # Register the new notebook in redis
        is_inserted = self.r.hsetnx(hash_main, entity.foreign_language, new_sentence)

        # Checks if a notebook was inserted        
        if not is_inserted:
            raise Exception(f'The Sentence "{entity.foreign_language}" already exists. Choice another sentence to list!')
        
        self.set_map_id_name(entity)
        self.set_sentence_id_sequence()

        return entity


    def get_all(self, entity: Sentence) -> List[Sentence]:
        pass


    def get_by_id(self, entity: Sentence) -> Sentence:
        hash_main_sentence_id = f'{entity.__class__.__name__}_id'
        hash_main_sentence = entity.__class__.__name__

        hash_key = self.r.hget(hash_main_sentence_id, entity.id)
        resp = self.r.hget(hash_main_sentence, hash_key)

        if not (hash_key and resp):
            return None
            # raise Exception(f'There is no a sentence with id={entity.id}!')

        data = json.loads(resp)

        sentence = Sentence()

        sentence.id = data['id']
        sentence.created_at = data['created_at']
        sentence.foreign_language = data['foreign_language']
        sentence.mother_tongue = data['mother_tongue']
        sentence.foreign_idiom = data['foreign_idiom']
        sentence.mother_idiom = data['mother_idiom']

        return sentence


    def update(self, entity: Sentence) -> List[Sentence]:
        pass


    def find_by_field(self, entity: Sentence) -> List[Sentence]:
        filters = dict([v for v in vars(entity).items() if not v[0].startswith('_') and bool(v[-1])])
        for attr, value in filters.items():
            if not bool(value): continue

            if attr in 'foreign_language':
                break
        else:
            raise Exception(f'This field "{attr}" cannot be used to find PageSection objects!')

        hash_main = entity.__class__.__name__
        hash_key = value

        resp = self.r.hget(hash_main, hash_key)

        if resp is None:
            return []
        
        data = json.loads(resp)
        
        sentence_list = [
            Sentence(
                id_=data.get('id'),
                created_at=data.get('created_at'),
                foreign_language=data.get('foreign_language'),
                mother_tongue=data.get('mother_tongue'),
                foreign_idiom=data.get('foreign_idiom'),
                mother_idiom=data.get('mother_idiom')                
            )
        ]
        
        return sentence_list


    def delete(self, entity: Sentence) -> bool:
        pass

    def set_map_id_name(self, entity: Sentence):
        hash_main = f'{entity.__class__.__name__}_id'
        self.r.hsetnx(hash_main, entity.id, entity.foreign_language)

    def set_sentence_id_sequence(self):
        key_sequence = 'sentence_id_sequence'        
        if not self.r.exists(key_sequence):
            self.r.set(key_sequence, 0)
        self.r.incr(key_sequence)

    def get_sentence_id_sequence(self):
        key_sequence = 'sentence_id_sequence'        
        if not self.r.exists(key_sequence):
            self.r.set(key_sequence, 1)
        new_id = self.r.get(key_sequence)
        return new_id




if __name__ == '__main__':

    notebook = Notebook(id_=1)
    page_section_filter = PageSection(
        created_at=datetime.datetime.now().date(),
        notebook=notebook,
        group=Group.A
    )

    page_section_dao = PageSectionDAO()
    result = page_section_dao.find_by_field(page_section_filter)

    print(page_section_dao.__class__, len(result))
