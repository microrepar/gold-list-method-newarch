import datetime
import os.path
from pathlib import Path
from typing import List

import pandas as pd

from src.core.dao import AbstractDAO
from src.model import Group, Notebook, PageSection, Sentence

# The directory containing this file
HERE = os.path.abspath(os.path.dirname(__file__))

notebook_file = Path(HERE).parent / 'data_base' / 'notebook.parquet'
notebook_columns = ['id', 'name', 'created_at', 'updated_at', 'list_size', 'days_period', 'foreign_idiom', 'mother_idiom']
notebook_types = ['int64', str, 'datetime64[ns]', 'datetime64[ns]', 'Int64', 'Int64', str, str]
if not notebook_file.exists():
    df = pd.DataFrame(columns=notebook_columns)
    df = df.astype(dict(zip(notebook_columns, notebook_types)))
    df.to_parquet(notebook_file, index=False)


page_section_file = Path(HERE).parent / 'data_base' / 'page_section.parquet'
page_section_columns = ['id',    'created_at',       'section_number',   'page_number',  'created_by_id',    'group',    'distillation_at', 'distillation_actual', 'distillated', 'memorized',   'translated_sentence', 'sentence_id',   'notebook_id']
page_section_types   = ['Int64', 'datetime64[ns]',    'Int64',            'Int64',        'Int64',            str,        'datetime64[ns]',  'datetime64[ns]',       bool,         bool,          str,                    'Int64',        'Int64']
if not page_section_file.exists():
    df = pd.DataFrame(columns=page_section_columns)
    df = df.astype(dict(zip(page_section_columns, page_section_types)))
    df.to_parquet(page_section_file, index=False)


sentence_file = Path(HERE).parent / 'data_base' / 'sentence.parquet'
sentence_columns = ['id', 'created_at', 'foreign_language', 'mother_tongue', 'foreign_idiom', 'mother_idiom',]
sentence_types = ['Int64', 'datetime64[ns]', str, str, str, str]
if not sentence_file.exists():
    df = pd.DataFrame(columns=sentence_columns)
    df = df.astype(dict(zip(sentence_columns, sentence_types)))
    df.to_parquet(sentence_file, index=False)



class NotebookDAO(AbstractDAO):

    def insert(self, entity: Notebook) -> Notebook:
        # Load notebook dataframe by notebook_file
        df = pd.read_parquet(notebook_file)

        # Checks if exists a notebook with same name
        has_notebook = df[df['name'].str.upper() == entity.name.upper()]['name'].to_list()
        if has_notebook:
            raise Exception(f'Notebook name "{entity.name}" already exists. Choice another name to notebook')
        
        # Checks maximum id that exist in the notebook dataframe
        if df.empty:
            new_id = 1
        else:
            new_id = df['id'].max() + 1

        # Add maximum id that exist in the notebook dataframe plus 1 into notebook object id 
        entity.id = new_id

        # Registry new notebook into dataframe using pd.concat method 
        df_registro = pd.DataFrame(entity.data_to_dataframe())
        df_concat = pd.concat([df, df_registro], ignore_index=True)

        df_concat.to_parquet(notebook_file)

        return entity


    def get_all(self, entity: Notebook=None) -> List[Notebook]:
        df_notebook = pd.read_parquet(notebook_file)

        page_section_dao = PageSectionDAO()
        
        notebook_list = []
        for index, row in df_notebook.iterrows():
            notebook_filter = Notebook(id_=row['id'])
            page_section_filter = PageSection(notebook=notebook_filter)
            page_section_list = page_section_dao.find_by_field(page_section_filter)

            notebook_list.append(
                Notebook(name=row['name'],
                         id_=row['id'],
                         created_at=row['created_at'],
                         updated_at=row['updated_at'],
                         list_size=row['list_size'],
                         days_period=row['days_period'],
                         foreign_idiom=row['foreign_idiom'],
                         mother_idiom=row['mother_idiom'],
                         page_section_list=page_section_list
                )
            )

        return notebook_list

    def get_by_id(self, entity: Notebook) -> Notebook:
        df = pd.read_parquet(notebook_file)

        df_result = df[df['id'] == entity.id]

        if df_result.empty:
            return None

        notebook = Notebook()
        for index, row in df_result.iterrows():            

            notebook.id = row['id']
            notebook.name = row['name']
            notebook.created_at = row['created_at']
            notebook.updated_at = row['updated_at']
            notebook.list_size = row['list_size']
            notebook.days_period = row['days_period']
            notebook.foreign_idiom = row['foreign_idiom']
            notebook.mother_idiom = row['mother_idiom']
            

        return notebook


    def update(self, entity: Notebook) -> Notebook:
        pass


    def find_by_field(self, entity: Notebook) -> List[Notebook]:
        pass


    def delete(self, entity: Notebook) -> bool:
        pass
    


class PageSectionDAO(AbstractDAO):

    def insert(self, entity: PageSection) -> PageSection:
        df = pd.read_parquet(page_section_file)

        if entity.created_at:
            # Checks if the group already exists on the same date
            check_page_section = PageSection(group=entity.group, 
                                            created_at=entity.created_at,
                                            notebook=entity.notebook)
            
            page_section_result_list = self.find_by_field(check_page_section)        

            if len(page_section_result_list) > 0:
                raise Exception(f'There is already a page for the group {entity.group.value} and selected day {entity.created_at}!')

        if df.empty:
            next_section_number = 1
            next_id = 1
        else:
            next_section_number = df['section_number'].max() + 1
            next_id = df['id'].max() + 1
        
        if not next_section_number:
            next_section_number = 1

        if not next_id:
            next_id = 1

        # Add maximum id that exist in the page_section dataframe plus 1 into page_section object id 
        page_section = PageSection()
        page_section.set_id(next_id)
        page_section.section_number = next_section_number

        page_section.created_by = entity.created_by
        page_section.page_number = entity.page_number
        page_section.group = entity.group
        page_section.created_at = entity.created_at
        page_section.distillation_at = entity.distillation_at
        page_section.distillated = entity.distillated
        page_section.sentences = entity.sentences
        page_section.translated_sentences = entity.translated_sentences
        page_section.memorializeds = entity.memorializeds
        page_section.notebook = entity.notebook

        # Registry new page_section into dataframe using pd.concat method 
        df_registro = pd.DataFrame(page_section.data_to_dataframe())
        df_concat = pd.concat([df, df_registro], ignore_index=True)

        df_concat.to_parquet(page_section_file)

        return page_section
    

    def get_all(self, entity: PageSection) -> List[PageSection]:
        pass

    def get_by_id(self, entity: PageSection) -> PageSection:
        df = pd.read_parquet(page_section_file)

        df_result = df[df['section_number'] == entity.section_number]

        if df_result.empty:
            return None

        sentence_dao = SentenceDAO()
        notebook_dao = NotebookDAO()        

        sentence_id_list         = []
        translated_sentence_list = []
        memorized_list           = []
        id_list                  = []
        for index, row in df_result.iterrows():
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
         
            page_section = PageSection(
                id_                  = min(id_list),
                section_number          = row['section_number'],
                created_at           = row['created_at'],                    
                group                = Group(row['group']),
                distillation_at      = row['distillation_at'],
                distillation_actual   = row['distillation_actual'],
                distillated          = row['distillated'],
                memorializeds        = memorized_list,
                translated_sentences = translated_sentence_list,
                sentences            = sentences,
                notebook             = notebook
            )
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



class SentenceDAO(AbstractDAO):

    def insert(self, entity: Sentence) -> Sentence:
         # Load sentence dataframe by sentence_file
        df = pd.read_parquet(sentence_file)

        # Checks maximum id that exist in the sentence dataframe
        if df.empty:
            new_id = 1
        else:
            new_id = df['id'].max() + 1

        # Add maximum id that exist in the sentence dataframe plus 1 into sentence object id 
        entity.id = new_id

        # Registry new sentence into dataframe using pd.concat method 
        df_registro = pd.DataFrame(entity.data_to_dataframe())
        df_concat = pd.concat([df, df_registro], ignore_index=True)

        df_concat.to_parquet(sentence_file)

        return entity

    def get_all(self, entity: Sentence) -> List[Sentence]:
        pass

    def get_by_id(self, entity: Sentence) -> Sentence:
        df = pd.read_parquet(sentence_file)

        sentence = Sentence()

        df_result = df[df['id'] == entity.id]

        if df_result.empty:
            return None

        for index, row in df_result.iterrows():
            sentence.id = row['id']
            sentence.created_at = row['created_at']
            sentence.foreign_language = row['foreign_language']
            sentence.mother_tongue = row['mother_tongue']
            sentence.foreign_idiom = row['foreign_idiom']
            sentence.mother_idiom = row['mother_idiom']

        return sentence


    def update(self, entity: Sentence) -> List[Sentence]:
        pass


    def find_by_field(self, entity: Sentence) -> List[Sentence]:
        df = pd.read_parquet(sentence_file)
        df_result = df.copy()

        sentence_dao = SentenceDAO()
        
        filters = dict([v for v in vars(entity).items() if not v[0].startswith('_') and bool(v[-1])])
        for attr, value in filters.items():
            if not bool(value): continue

            if isinstance(value, datetime.date):
                value = pd.to_datetime(value).strftime("%Y-%m-%d")
            elif attr in 'foreign_language id mother_tongue foreign_idiom mother_idiom':
                ...
            else:
                raise Exception(f'This field "{attr}" cannot be used to find PageSection objects!')

            df_result = df_result[df_result[attr] == value]

        if df_result.empty:
            return []
        
        sentence_list = []
        for index, row in df_result.iterrows():
            sentence_filter = Sentence(id_=row['id'])
            found_sentence = sentence_dao.get_by_id(sentence_filter)

            if found_sentence:
                sentence_list.append(
                    found_sentence
                )
        
        return sentence_list


    def delete(self, entity: Sentence) -> bool:
        pass




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
