import datetime

from src.core.dao_redis import PageSectionDAO, SentenceDAO
from src.model import Group, PageSection, Sentence


def build_page_section_with_sentence_list(*, 
                                          dataframe, 
                                          selected_day, 
                                          notebook, 
                                          group: Group, 
                                          persit=False) -> PageSection:
    sentence_dao = SentenceDAO()
    page_section_dao = PageSectionDAO()

    memorized_list  = []
    translated_list = []
    sentence_list   = []

    for index, row in dataframe.iterrows():
        memorized_list.append(
            row['remembered']
        )

        translated_list.append(
            row['translated_sentence']
        )

        sentence_filter = Sentence(foreign_language=row['foreign_language'])
        sentence_found_list = sentence_dao.find_by_field(sentence_filter)
        
        if sentence_found_list and isinstance(sentence_found_list[-1], Sentence):
            sentence_list.append(sentence_found_list[-1])
        else:
            sentence = sentence_dao.insert(
                Sentence(
                    created_at=datetime.datetime.strptime(str(selected_day), '%Y-%m-%d').date(),
                    foreign_language=row['foreign_language'], 
                    mother_tongue=row['mother_tongue'], 
                    foreign_idiom=notebook.foreign_idiom, 
                    mother_idiom=notebook.mother_idiom                
                )
            )
            sentence_list.append(
                sentence
            )

    page_section = PageSection(
        group=group,
        created_at=datetime.datetime.strptime(str(selected_day), '%Y-%m-%d').date(),
        distillation_at=(datetime.datetime.strptime(str(selected_day), '%Y-%m-%d') + datetime.timedelta(days=notebook.days_period)).date(),
        notebook=notebook,
        sentences=sentence_list, 
        memorializeds=memorized_list,
        translated_sentences=translated_list
    )

    if persit:
        page_section_result = page_section_dao.insert(page_section)
        return page_section_result
    
    return page_section
        