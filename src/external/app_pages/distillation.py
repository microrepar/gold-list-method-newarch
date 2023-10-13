import datetime

import pandas as pd
import streamlit as st
from st_pages import add_page_title

from src.adapters import Controller
from src.core.notebook import Notebook
from src.core.pagesection import PageSection, Group

st.set_page_config(layout='wide')

placeholder_container_msg = st.container()


add_page_title()  # Optional method to add title and icon to current page

def get_group_dataframe(selected_day, group: Group):

    pagesection = notebook.get_page_section(distillation_at=selected_day,
                                            group=group)

    sentences  = None if pagesection is None else pagesection.sentences
    
    columns = [
        "foreign_language",
        "translated_sentences",
        "remembered",
        "mother_tongue"]
    
    df = pd.DataFrame(columns=columns) if sentences is None \
        else pd.concat([pd.DataFrame(s.data_to_dataframe()) for s in sentences])


    if pagesection:
        df['translated_sentences'] = pagesection.translated_sentences
        df['remembered'] = pagesection.memorializeds
    else:
        df['translated_sentences'] = ''
        df['remembered'] = False        
    
    return df, pagesection


#############################################################
controller = Controller()
request = {
    'resource': '/notebook'
}
resp = controller(request=request)
notebook_list = resp.get('entities')
messages = resp.get('messages')

for msg in messages:
    placeholder_container_msg.error(msg, icon="🚨")

#############################################################

notebook_dict = {n.name: n for n in notebook_list}

if len(notebook_list) > 0:
    selected_notebook = st.sidebar.selectbox('**SELECT NOTEBOOK:**', 
                                             [n.name for n in notebook_list],
                                             key='select_notebook')
    

    notebook: Notebook = notebook_dict.get(selected_notebook)

    placeholder_subtitle = st.empty()

    col_group_1, col_group_2, col_group_3, col_group_4 = st.sidebar.columns(4)

    selected_day = st.sidebar.date_input('**LIST OF THE DAY:**', 
                                         datetime.datetime.now().date(), 
                                         format='DD/MM/YYYY')
    
    choiced_group = st.sidebar.radio('SELECT GROUP:', ('GROUP A', 'GROUP B', 'GROUP C', 'GROUP D'))
    dataframe, page_section_group = get_group_dataframe(selected_day, 
                                                        Group(choiced_group.split()[-1]))
    placeholder_subtitle.subheader(f'{notebook.name.upper()} NOTEBOOK - {choiced_group}')

    st.sidebar.markdown("[Show Calendar](Calendar)")

    column_configuration = {
        "foreign_language": st.column_config.TextColumn(
            "Foreign Language", 
            help="Read aloud the sentece or word just once",
            width="large"
        ),
        "translated_sentence": st.column_config.TextColumn(
            "Translation", 
            help="Write the sentece or word in your mother tongue",
            width="large"
        ),
        "remembered": st.column_config.CheckboxColumn(
            "You remember?", 
            help="Check the checkbox if you remembered this sentence?",
            width='small'
        ),
    }

    rename_columns = {
        'remembered': 'You remember?',
        'foreign_language':'Foreign Language',
        'translated_sentences': 'Translate Sentence',
        'mother_tongue': 'Mother Tongue'
    }

    
##########################Group Section####################################

    distilled_columns = ['remembered', 'foreign_language', 'mother_tongue', 'translated_sentences', ]
    
    btn_update = False
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        read_aloud = st.checkbox('Read aloud', value=True, 
                                    key='read_aloud', disabled=True)
    with col2:
        translate = st.checkbox('Translate', value=True, 
                                    key='translate', disabled=True)
    with col3:
        placeholder_checkbox_distill = st.empty()
        if  page_section_group and page_section_group.distillated:
            distill = placeholder_checkbox_distill.checkbox(
                'Distill', key='distill', value=True, disabled=True
            )
        else:
            distill = placeholder_checkbox_distill.checkbox(
                'Distill', key='distill', value=False, disabled=False
            )
    
    col4.markdown(f'Date: {selected_day}')


    
    if not dataframe.empty:
    
        if read_aloud and not translate and not distill:
            df_distilled = st.data_editor(
                dataframe[['foreign_language']],
                column_config=column_configuration,
                use_container_width=True,
                hide_index=True,
                num_rows="fixed",
                disabled=['foreign_language', 'mother_tongue'],
                key='read_aloud_data')
        elif translate and not distill:
            df_distilled = st.data_editor(
                dataframe[['foreign_language', 'translated_sentences']],
                column_config=column_configuration,
                use_container_width=True,
                hide_index=True,
                num_rows="fixed",
                disabled=['foreign_language'] if not page_section_group.distillated \
                    else ['translated_sentences', 'foreign_language'],
                key='translate_data')
            
            btn_update = st.button('RECORD TRANSLATION',
                                   use_container_width=True, 
                                   type='secondary', 
                                   key='btn_record_group_a')
        
        elif distill and not page_section_group.distillated:
            
            df_distilled = st.data_editor(
                dataframe[distilled_columns],
                column_config=column_configuration,
                use_container_width=True,
                hide_index=True,
                num_rows="fixed",
                disabled=['foreign_language', 'mother_tongue', 'translated_sentences'] \
                                if not page_section_group.distillated \
                                else distilled_columns,
                key='distill_data')

        elif page_section_group.distillated:
            st.dataframe(
                dataframe[distilled_columns].rename(columns=rename_columns),
                use_container_width=True, hide_index=True)
        
        
        if btn_update:
            
            df_update = df_distilled.copy().reset_index(drop=True)
            df_update['remembered'] = False
            df_update['foreign_idiom'] = notebook.foreign_idiom
            df_update['mother_idiom'] = notebook.mother_idiom
            df_update['created_at'] = selected_day

            ###############################################################
            # UPDATE PAGESECTION - BODY REQUEST
            ###############################################################
            cols_to_rename = {
                "foreign_language":"sentence_foreign_language",
                "mother_tongue":"sentence_mother_tongue",
                "foreign_idiom":"sentence_foreign_idiom",
                "mother_idiom":"sentence_mother_idiom",
                "created_at":"sentence_created_at",
            }
            df_update.rename(columns=cols_to_rename, inplace=True)


            request = {
                'resource': '/pagesection/update',
                'pagesection_notebook': {'notebook_id_': notebook.id,
                                        'notebook_days_period': notebook.days_period},
                'pagesection_id_': page_section_group.id,
                'pagesection_page_number': page_section_group.page_number,
                'pagesection_group': page_section_group.group,
                'pagesection_created_at': page_section_group.created_at,
                'pagesection_distillation_at': page_section_group.distillation_at,
                'pagesection_translated_sentences': df_update['translated_sentences'].to_list(),
                'pagesection_memorializeds': df_update['remembered'].to_list(),
                'pagesection_sentences': list(df_update.T.to_dict().values()),            
            }
            ####################
            # FrontController
            ####################
            resp = controller(request=request)
            messages = resp.get('messages')
            entities = resp.get('entities')

            ####################
            # Feadback
            ####################
            if messages:
                for msg in messages:
                    placeholder_container_msg.error(msg,  icon="🚨")
                st.toast('Something went wrong!')
            elif entities:
                page_section_group = entities[-1]
                placeholder_container_msg.success(f'{entities[-1]} was updated successfully!')
                placeholder_container_msg.empty()
                st.toast('Page section was updated successfully.')
            ###############################################################
            ###############################################################

        if distill:
            placeholder_distill_button = st.empty()

            if placeholder_distill_button.button('HEADLIST DISTILLATION FINISH',
                                                 use_container_width=True, 
                                                 type='primary', 
                                                 key='btn_distill',
                                                 disabled=True if page_section_group.distillated \
                                                    else False):
                
                df_distilled = df_distilled.reset_index(drop=True)
                df_distilled['foreign_idiom'] = notebook.foreign_idiom
                df_distilled['mother_idiom'] = notebook.mother_idiom

                ###############################################################
                # DISTILLATION PAGESECTION - BODY REQUEST
                ###############################################################
                cols_to_rename = {
                    "foreign_language":"sentence_foreign_language",
                    "mother_tongue":"sentence_mother_tongue",
                    "foreign_idiom":"sentence_foreign_idiom",
                    "mother_idiom":"sentence_mother_idiom",
                }
                df_distilled.rename(columns=cols_to_rename, inplace=True)

                request = {
                    'resource': '/pagesection/distillation',
                    'pagesection_notebook': {'notebook_id_': notebook.id,
                                            'notebook_days_period': notebook.days_period},
                    'pagesection_id_': page_section_group.id,
                    'pagesection_page_number': page_section_group.page_number,
                    'pagesection_group': page_section_group.group,
                    'pagesection_created_at': selected_day,
                    'pagesection_distillation_at': page_section_group.distillation_at,
                    'pagesection_translated_sentences': df_distilled['translated_sentences'].to_list(),
                    'pagesection_memorializeds': df_distilled['remembered'].to_list(),
                    'pagesection_sentences': list(df_distilled.T.to_dict().values()),            
                }
                ####################
                # FrontController
                ####################
                resp = controller(request=request)
                messages = resp.get('messages')
                entities = resp.get('entities')

                ####################
                # FeedBack
                ####################
                if messages:
                    for msg in messages:
                        placeholder_container_msg.error(msg,  icon="🚨")
                    st.toast('Something went wrong!')
                elif entities:
                    page_section_after_a = entities[-1]
                    notebook.page_section_list.append(page_section_after_a)

                    st.toast('Distillation was saved!')
                    placeholder_container_msg.success(f'{page_section_after_a} was distilled successfully!')
                    
                    placeholder_distill_button.button('HEADLIST DISTILLATION FINISH', 
                                                        use_container_width=True, 
                                                        type='primary', 
                                                        key='btn_distillated',
                                                        disabled=True)
                    placeholder_checkbox_distill.checkbox('Distill', 
                                                          value=True, 
                                                          disabled=True,
                                                          key='cbox_distillated')

                
    else:
        st.warning('⚠️There is no a list of expressions '
                    'in "Group A" to distill on the selected day!')

else:
    st.warning('⚠️Attention! There are no notebooks registred!')
    st.markdown('[Create a Notebook](Add%20Notebook)')
 