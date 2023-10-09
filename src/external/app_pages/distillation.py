import datetime

import pandas as pd
import streamlit as st
from st_pages import add_page_title

from src.adapters import Controller
from src.core.notebook import Notebook
from src.core.pagesection import PageSection, Group

st.set_page_config(layout='wide')

placeholder_container_msg = st.container()
# placeholder_container_msg.empty()

add_page_title()  # Optional method to add title and icon to current page


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
    selected_notebook = st.sidebar.selectbox('**NOTEBOOK:**', 
                                             [n.name for n in notebook_list],
                                             key='select_notebook')

    notebook: Notebook = notebook_dict.get(selected_notebook)

    st.title(f'NOTEBOOK - {notebook.name.upper()}')

    col_group_1, col_group_2, col_group_3, col_group_4 = st.sidebar.columns(4)
    st.sidebar.markdown("[Add New Headlist](Add%20HeadList)")

    st.sidebar.divider()

    selected_day = st.sidebar.date_input('**LIST OF THE DAY:**', 
                                         datetime.datetime.now().date(), 
                                         format='DD/MM/YYYY')

    page_section_group_a = notebook.get_page_section(distillation_at=selected_day, 
                                                     group=Group.HEADLIST)
    page_section_group_b = notebook.get_page_section(distillation_at=selected_day, 
                                                     group=Group.B)
    page_section_group_c = notebook.get_page_section(distillation_at=selected_day, 
                                                     group=Group.C)
    page_section_group_d = notebook.get_page_section(distillation_at=selected_day, 
                                                     group=Group.D)

    sentences_a  = None if page_section_group_a is None \
        else page_section_group_a.sentences
    sentences_b = None if page_section_group_b is None \
        else page_section_group_b.sentences
    sentences_c = None if page_section_group_c is None \
        else page_section_group_c.sentences
    sentences_d = None if page_section_group_d is None \
        else page_section_group_d.sentences
    
    columns = [
        "foreign_language",
        "translated_sentence",
        "remembered",
        "mother_tongue"]
    
    dfa = pd.DataFrame(columns=columns) if sentences_a is None \
        else pd.concat([pd.DataFrame(s.data_to_dataframe()) for s in sentences_a])
    dfb = pd.DataFrame(columns=columns) if sentences_b is None \
        else pd.concat([pd.DataFrame(s.data_to_dataframe()) for s in sentences_b])
    dfc = pd.DataFrame(columns=columns) if sentences_c is None \
        else pd.concat([pd.DataFrame(s.data_to_dataframe()) for s in sentences_c])
    dfd = pd.DataFrame(columns=columns) if sentences_d is None \
        else pd.concat([pd.DataFrame(s.data_to_dataframe()) for s in sentences_d])


    if page_section_group_a:
        dfa['translated_sentences'] = page_section_group_a.translated_sentences
        dfa['remembered'] = page_section_group_a.memorializeds
    else:
        dfa['translated_sentences'] = ''
        dfa['remembered'] = False        
    
    if page_section_group_b:
        dfb['translated_sentences'] = page_section_group_b.translated_sentences
        dfb['remembered'] = page_section_group_b.memorializeds
    else:
        dfb['translated_sentences'] = ''
        dfb['remembered'] = False
    
    if page_section_group_c:
        dfc['translated_sentences'] = page_section_group_c.translated_sentences
        dfc['remembered'] = page_section_group_c.memorializeds
    else:
        dfc['translated_sentences'] = ''
        dfc['remembered'] = False
    
    if page_section_group_d:
        dfd['translated_sentences'] = page_section_group_d.translated_sentences
        dfd['remembered'] = page_section_group_d.memorializeds
    else:
        dfd['translated_sentences'] = ''
        dfd['remembered'] = False
    

    column_configuration = {
        "foreign_language": st.column_config.TextColumn(
            "Foreign Language", 
            help="Read aloud the sentece or word just once",
            width="medium"
        ),
        "translated_sentence": st.column_config.TextColumn(
            "Translation", 
            help="Write the sentece or word in your mother tongue",
            width="medium"
        ),
        "remembered": st.column_config.CheckboxColumn(
            "You remember?", 
            help="Check the checkbox if you remembered this sentence?",
            width='small'
        ),
    }

    btn_update_a = False
    btn_update_b = False
    btn_update_c = False
    btn_update_d = False

    rename_columns = {
        'remembered': 'You remember?',
        'foreign_language':'Foreign Language',
        'translated_sentences': 'Translate Sentence',
        'mother_tongue': 'Mother Tongue'
    }

    tab1, tab2, tab3, tab4 = st.tabs([':violet[**HeadLits/Group A**]', ':violet[**Group B**]', ':violet[**Group C**]', ':violet[**Group D**]'])
    distilled_columns = ['remembered', 'foreign_language', 'mother_tongue', 'translated_sentences', ]
##########################GroupA Section####################################
    with tab1:
        placehold_data_edit_headlist = st.empty()
        with placehold_data_edit_headlist:
            placehold_container_dt_edit_headlist = st.container()
            with placehold_container_dt_edit_headlist:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    read_aloud_a = st.checkbox('Read aloud', value=True, 
                                               key='read_aloud_a', disabled=True)
                with col2:
                    translate_a = st.checkbox('Translate', value=True, 
                                              key='translate_a', disabled=True)
                with col3:
                    distill_a = st.checkbox('Distill', key='distill_a',
                                            value=True if page_section_group_a \
                                                and page_section_group_a.distillated else False,
                                            disabled=True if page_section_group_a \
                                                and page_section_group_a.distillated else False)
                col4.markdown(f'Date: {selected_day}')
        if not dfa.empty:
        
            if read_aloud_a and not translate_a and not distill_a:
                dfa_distilled = placehold_container_dt_edit_headlist.data_editor(
                    dfa[['foreign_language']],
                    column_config=column_configuration,
                    use_container_width=True,
                    hide_index=True,
                    num_rows="fixed",
                    disabled=['foreign_language', 'mother_tongue'],
                    key='dt_edit_group_a'
                )
            elif translate_a and not distill_a:
                dfa_distilled = placehold_container_dt_edit_headlist.data_editor(
                    dfa[['foreign_language', 'translated_sentences']],
                    column_config=column_configuration,
                    use_container_width=True,
                    hide_index=True,
                    num_rows="fixed",
                    disabled=['foreign_language'] if not page_section_group_a.distillated \
                        else ['translated_sentences', 'foreign_language'],
                    key='dt_edit_group_a'
                )
                btn_update_a = placehold_container_dt_edit_headlist.button('RECORD HEADLIST TRANSLATION', 
                                                                        use_container_width=True, 
                                                                        type='secondary', 
                                                                        key='btn_record_group_a')
            
            elif distill_a and not page_section_group_a.distillated:
                
                dfa_distilled = placehold_container_dt_edit_headlist.data_editor(
                    dfa[distilled_columns],
                    column_config=column_configuration,
                    use_container_width=True,
                    hide_index=True,
                    num_rows="fixed",
                    disabled=['foreign_language', 'mother_tongue', 'translated_sentences'] \
                                    if not page_section_group_a.distillated \
                                    else distilled_columns,
                    key='dt_edit_group_a'
                )
            elif page_section_group_a.distillated:
                placehold_container_dt_edit_headlist.dataframe(
                    dfa[distilled_columns].rename(columns=rename_columns),
                    use_container_width=True, hide_index=True)
            
            if btn_update_a:
                
                dfa_update = dfa_distilled.copy()
                dfa_update['remembered'] = False
                dfa_update['foreign_idiom'] = notebook.foreign_idiom
                dfa_update['mother_idiom'] = notebook.mother_idiom
                dfa_update['created_at'] = selected_day

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
                dfa_update.rename(columns=cols_to_rename, inplace=True)

                request = {
                    'resource': '/pagesection/update',
                    'pagesection_notebook': {'notebook_id_': notebook.id,
                                            'notebook_days_period': notebook.days_period},
                    'pagesection_id_': page_section_group_a.id,
                    'pagesection_group': page_section_group_a.group,
                    'pagesection_created_at': selected_day,
                    'pagesection_translated_sentences': dfa_update['translated_sentences'].to_list(),
                    'pagesection_memorializeds': dfa_update['remembered'].to_list(),
                    'pagesection_sentences': list(dfa_update.T.to_dict().values()),            
                }

                # FrontController
                resp = controller(request=request)
                messages = resp.get('messages')
                entities = resp.get('entities')

                # FeedBack
                if messages:
                    for msg in messages:
                        placeholder_container_msg.error(msg,  icon="🚨")
                        st.toast('Something went wrong!')
                elif entities:
                    page_section_group_a
                    placeholder_container_msg.success(f'{entities[-1]} was updated successfully!')
                    placeholder_container_msg.empty()
                    st.toast('Page section was updated successfully.')

                ###############################################################


                # page_section_update_a: PageSection = build_page_section_with_sentence_list(dataframe=dfa_update,
                #                                             selected_day=page_section_group_a.created_at, 
                #                                             notebook=notebook, 
                #                                             group=page_section_group_a.group,
                #                                             persit=False)
                # page_section_group_a.translated_sentences  = page_section_update_a.translated_sentences
                # page_section_update_a.section_number = page_section_group_a.section_number
                # try:
                #     page_section_dao.update(page_section_update_a)
                #     st.toast('The translation of sentences has been updated!')
                # except Exception as error:
                #         placeholder_container_msg.error(str(error), icon="🚨")

            if distill_a:
                if placehold_container_dt_edit_headlist.button('HEADLIST DISTILLATION FINISH', 
                                                            use_container_width=True, 
                                                            type='primary', 
                                                            key='btn_group_a',
                                                            disabled=True if page_section_group_a.distillated \
                                                                                else False):
                    try:
                        page_section_update_a: PageSection = build_page_section_with_sentence_list(dataframe=dfa_distilled,
                                                            selected_day=page_section_group_a.created_at, 
                                                            notebook=notebook, 
                                                            group=page_section_group_a.group,
                                                            persit=False)
                        page_section_update_a.section_number = page_section_group_a.section_number
                        page_section_update_a.distillated = True
                        page_section_dao.update(page_section_update_a)
                        st.toast('Saving the distillation...')
                        
                        dfa_base = dfa_distilled[dfa_distilled['remembered'] == False].copy()
                        dfa_base['translated_sentences'] = ''
                        page_section_after_a = build_page_section_with_sentence_list(dataframe=dfa_base,
                                                            selected_day=selected_day, 
                                                            notebook=notebook, 
                                                            group=Group.B,
                                                            persit=False)
                        page_section_after_a.set_created_by(page_section_group_a)
                        page_section_after_a = page_section_dao.insert(page_section_after_a)
                        
                        st.toast('Distillation was saved!')
                        placehold_data_edit_headlist.success(f'{page_section_after_a} was inserted successfully!')
                        notebook.page_section_list.append(page_section_after_a)
                    except Exception as error:
                        placeholder_container_msg.error(str(error), icon="🚨")
                        st.toast('Something went wrong!')
                        if 'There is already a page'.upper() in str(error).upper():
                            st.error(str(error), icon="🚨")
        else:
            placehold_data_edit_headlist.warning('⚠️There is no a list of expressions '
                                                 'in "Group A" to distill on the selected day!')
    

# ##########################GroupB Section####################################
#     with tab2:
#         placehold_data_edit_group_b = st.empty()
#         with placehold_data_edit_group_b:
#             placehold_container_dt_edit_group_b = st.container()
#             with placehold_container_dt_edit_group_b:
#                 col1, col2, col3, col4 = st.columns(4)
#                 with col1:
#                     read_aloud_b = st.checkbox('Read aloud', value=True, key='read_aloud_b', disabled=True)
#                 with col2:
#                     translate_b = st.checkbox('Translate', value=True, key='translate_b', disabled=True)
#                 with col3:
#                     distill_b = st.checkbox('Distill', key='distill_b',
#                                             value=True if page_section_group_b \
#                                                 and page_section_group_b.distillated else False,
#                                             disabled=True if page_section_group_b \
#                                                 and page_section_group_b.distillated else False)
#                 col4.markdown(f'Date: {selected_day}')

#         if not dfb.empty:
#             if read_aloud_b and not translate_b and not distill_b:
#                 dfb_distilled = placehold_container_dt_edit_group_b.data_editor(
#                     dfb[['foreign_language']],
#                     column_config=column_configuration,
#                     use_container_width=True,
#                     hide_index=True,
#                     num_rows="fixed",
#                     disabled=['foreign_language'],
#                     key='dt_edit_group_b'
#                 )
#             elif translate_b and not distill_b:
#                 dfb_distilled = placehold_container_dt_edit_group_b.data_editor(
#                     dfb[['foreign_language', 'translated_sentences']],
#                     column_config=column_configuration,
#                     use_container_width=True,
#                     hide_index=True,
#                     num_rows="fixed",
#                     disabled=['foreign_language'],
#                     key='dt_edit_group_b'
#                 )

#                 btn_update_b = placehold_container_dt_edit_group_b.button('RECORD GROUP B TRANSLATION', 
#                                                                         use_container_width=True, 
#                                                                         type='secondary', 
#                                                                         key='btn_record_group_b')
            
#             elif distill_b and not page_section_group_b.distillated:
#                 dfb_distilled = placehold_container_dt_edit_group_b.data_editor(
#                     dfb[distilled_columns],
#                     column_config=column_configuration,
#                     use_container_width=True,
#                     hide_index=True,
#                     num_rows="fixed",
#                     disabled=['foreign_language', 'mother_tongue', 'translated_sentences'] \
#                                     if not page_section_group_b.distillated \
#                                     else distilled_columns,
#                     key='dt_edit_group_b'
#                 )
#             elif page_section_group_b.distillated:
#                 placehold_container_dt_edit_group_b.dataframe(
#                     dfb[distilled_columns].rename(columns=rename_columns),
#                     use_container_width=True, hide_index=True)
            
            
#             if btn_update_b:
#                 dfb_update = dfb_distilled.copy()
#                 dfb_update['remembered'] = False
#                 page_section_update_b: PageSection = build_page_section_with_sentence_list(dataframe=dfb_update,
#                                                             selected_day=page_section_group_b.created_at, 
#                                                             notebook=notebook, 
#                                                             group=page_section_group_b.group,
#                                                             persit=False)
#                 page_section_group_b.translated_sentences  = page_section_update_b.translated_sentences
#                 page_section_update_b.section_number = page_section_group_b.section_number
#                 try:
#                     page_section_dao.update(page_section_update_b)
#                     st.toast('The translation of sentences has been updated!')
#                 except Exception as error:
#                         placeholder_container_msg.error(str(error), icon="🚨")

#             if distill_b and not dfb.empty:
#                 if placehold_container_dt_edit_group_b.button('GROUP B DISTILLATION FINISH', 
#                                                             use_container_width=True, 
#                                                             type='primary', 
#                                                             key='btn_group_b',
#                                                             disabled=True if page_section_group_b.distillated \
#                                                                                 else False):
#                     try:
#                         page_section_update_b: PageSection = build_page_section_with_sentence_list(dataframe=dfb_distilled,
#                                                             selected_day=page_section_group_b.created_at, 
#                                                             notebook=notebook, 
#                                                             group=page_section_group_b.group,
#                                                             persit=False)
#                         page_section_update_b.section_number = page_section_group_b.section_number
#                         page_section_update_b.distillated = True
#                         page_section_dao.update(page_section_update_b)
#                         st.toast('Saving the distillation...')

#                         dfb_base = dfb_distilled[dfb_distilled['remembered'] == False].copy()
#                         dfb_base['translated_sentences'] = ''
#                         page_section_after_b = build_page_section_with_sentence_list(dataframe=dfb_base,
#                                                             selected_day=selected_day, 
#                                                             notebook=notebook, 
#                                                             group=Group.C,
#                                                             persit=False)
#                         page_section_after_b.set_created_by(page_section_group_b)
#                         page_section_after_b = page_section_dao.insert(page_section_after_b)
                        
#                         st.toast('Distillation was saved!')
#                         placehold_data_edit_group_b.success(f'{page_section_after_b} was inserted successfully!')

#                         notebook.page_section_list.append(page_section_after_b)
#                     except Exception as error:
#                         placeholder_container_msg.error(str(error), icon="🚨")
#                         if 'There is already a page'.upper() in str(error).upper():
#                             st.error(str(error), icon="🚨")
#         else:    
#             placehold_data_edit_group_b.warning('⚠️There is no a list of expressions '
#                                                 'in "Group B" to distill on the selected day!')
    


# ##########################GroupC Section####################################
#     with tab3:
#         placehold_data_edit_group_c = st.empty()
#         with placehold_data_edit_group_c:
#             placehold_container_dt_edit_group_c = st.container()
#             with placehold_container_dt_edit_group_c:
#                 col1, col2, col3, col4 = st.columns(4)
#                 with col1:
#                     read_aloud_c = st.checkbox('Read aloud', value=True, key='read_aloud_c', disabled=True)
#                 with col2:
#                     translate_c = st.checkbox('Translate', value=True, key='translate_c', disabled=True)
#                 with col3:
#                     distill_c = st.checkbox('Distill', key='distill_c',
#                                             value=True if page_section_group_c \
#                                                 and page_section_group_c.distillated else False,
#                                             disabled=True if page_section_group_c \
#                                                 and page_section_group_c.distillated else False)
#                 col4.markdown(f'Date: {selected_day}')
#         if not dfc.empty:
#             if read_aloud_c and not translate_c and not distill_c:
#                 dfc_distilled = placehold_container_dt_edit_group_c.data_editor(
#                     dfc[['foreign_language']],
#                     column_config=column_configuration,
#                     use_container_width=True,
#                     hide_index=True,
#                     num_rows="fixed",
#                     disabled=['foreign_language', 'mother_tongue'],
#                     key='dt_edit_group_c'
#                 )
#             elif translate_c and not distill_c:
#                 dfc_distilled = placehold_container_dt_edit_group_c.data_editor(
#                     dfc[['foreign_language', 'translated_sentences']],
#                     column_config=column_configuration,
#                     use_container_width=True,
#                     hide_index=True,
#                     num_rows="fixed",
#                     disabled=['foreign_language', 'mother_tongue'],
#                     key='dt_edit_group_c'
#                 )
#                 btn_update_c = placehold_container_dt_edit_group_c.button('RECORD GROUP C TRANSLATION', 
#                                                                         use_container_width=True, 
#                                                                         type='secondary', 
#                                                                         key='btn_record_group_c')
#             elif distill_c and not page_section_group_c.distillated:
#                 dfc_distilled = placehold_container_dt_edit_group_c.data_editor(
#                     dfc[distilled_columns],
#                     column_config=column_configuration,
#                     use_container_width=True,
#                     hide_index=True,
#                     num_rows="fixed",
#                     disabled=['foreign_language', 'mother_tongue'],
#                     key='dt_edit_group_c'
#                 )
#             elif page_section_group_c.distillated:
#                 placehold_container_dt_edit_group_c.dataframe(
#                     dfc[distilled_columns].rename(columns=rename_columns),
#                     use_container_width=True, hide_index=True)
            

#             if btn_update_c:
#                 dfc_update = dfc_distilled.copy()
#                 dfc_update['remembered'] = False
#                 page_section_update_c: PageSection = build_page_section_with_sentence_list(dataframe=dfc_update,
#                                                             selected_day=page_section_group_c.created_at, 
#                                                             notebook=notebook, 
#                                                             group=page_section_group_c.group,
#                                                             persit=False)
#                 page_section_group_c.translated_sentences  = page_section_update_c.translated_sentences
#                 page_section_update_c.section_number = page_section_group_c.section_number
#                 try:
#                     page_section_dao.update(page_section_update_c)
#                     st.toast('The translation of sentences has been updated!')
#                 except Exception as error:
#                         placeholder_container_msg.error(str(error), icon="🚨")

#             if distill_c and not dfc.empty:
#                 if placehold_container_dt_edit_group_c.button('GROUP C DISTILLATION FINISH', 
#                                                             use_container_width=True, 
#                                                             type='primary', 
#                                                             key='btn_group_c',
#                                                             disabled=True if page_section_group_c.distillated \
#                                                                                 else False):
#                     try:
#                         page_section_update_c: PageSection = build_page_section_with_sentence_list(dataframe=dfc_distilled,
#                                                             selected_day=page_section_group_c.created_at, 
#                                                             notebook=notebook, 
#                                                             group=page_section_group_c.group,
#                                                             persit=False)
#                         page_section_update_c.section_number = page_section_group_c.section_number
#                         page_section_update_c.distillated = True
#                         page_section_dao.update(page_section_update_c)
#                         st.toast('Saving the distillation...')

#                         dfc_base = dfc_distilled[dfc_distilled['remembered'] == False].copy()
#                         dfc_base['translated_sentences'] = ''
#                         page_section_after_c = build_page_section_with_sentence_list(dataframe=dfc_base,
#                                                             selected_day=selected_day, 
#                                                             notebook=notebook, 
#                                                             group=Group.D,
#                                                             persit=False)
#                         page_section_after_c.set_created_by(page_section_group_c)
#                         page_section_after_c = page_section_dao.insert(page_section_after_c)
                        
#                         st.toast('Distillation was saved!')
#                         placehold_data_edit_group_c.success(f'{page_section_after_c} was inserted successfully!')
#                         notebook.page_section_list.append(page_section_after_c)
#                     except Exception as error:
#                         placeholder_container_msg.error(str(error), icon="🚨")
#                         if 'There is already a page'.upper() in str(error).upper():
#                             st.error(str(error), icon="🚨")
#         else:
#             placehold_data_edit_group_c.warning('⚠️There is no a list of expressions '
#                                                 'in "Group C" to distill on the selected day!')
    

    
# ##########################GroupD Section####################################
#     with tab4:
#         placehold_data_edit_group_d = st.empty()
#         with placehold_data_edit_group_d:
#             placehold_container_dt_edit_group_d = st.container()
#             with placehold_container_dt_edit_group_d:
#                 col1, col2, col3, col4 = st.columns(4)
#                 with col1:
#                     read_aloud_d = st.checkbox('Read aloud', value=True, key='read_aloud_d', disabled=True)
#                 with col2:
#                     translate_d = st.checkbox('Translate', value=True, key='translate_d', disabled=True)
#                 with col3:
#                     distill_d = st.checkbox('Distill', key='distill_d',
#                                             value=True if page_section_group_d \
#                                                 and page_section_group_d.distillated else False,
#                                             disabled=True if page_section_group_d \
#                                                 and page_section_group_d.distillated else False)
#                 col4.markdown(f'Date: {selected_day}')

#         if not dfd.empty:
#             if read_aloud_d and not translate_d and not distill_d:
#                 dfd_distilled = placehold_container_dt_edit_group_d.data_editor(
#                     dfd[['foreign_language']],
#                     column_config=column_configuration,
#                     use_container_width=True,
#                     hide_index=True,
#                     num_rows="fixed",
#                     disabled=['foreign_language', 'mother_tongue'],
#                     key='dt_edit_group_d'
#                 )
#             elif translate_d and not distill_d:
#                 dfd_distilled = placehold_container_dt_edit_group_d.data_editor(
#                     dfd[['foreign_language', 'translated_sentences']],
#                     column_config=column_configuration,
#                     use_container_width=True,
#                     hide_index=True,
#                     num_rows="fixed",
#                     disabled=['foreign_language'] if page_section_group_d and not page_section_group_d.distillated \
#                         else ['translated_sentences', 'foreign_language'],
#                     key='dt_edit_group_d'
#                 )
#                 btn_update_d = placehold_container_dt_edit_group_d.button('RECORD GROUP D TRANSLATION', 
#                                                                         use_container_width=True, 
#                                                                         type='secondary', 
#                                                                         key='btn_record_group_d')
#             elif distill_d and not page_section_group_d.distillated:
#                 dfd_distilled = placehold_container_dt_edit_group_d.data_editor(
#                     dfd[distilled_columns],
#                     column_config=column_configuration,
#                     use_container_width=True,
#                     hide_index=True,
#                     num_rows="fixed",
#                     disabled=['foreign_language', 'mother_tongue'],
#                     key='dt_edit_group_d'
#                 )
#             elif page_section_group_d.distillated:
#                 placehold_container_dt_edit_group_d.dataframe(
#                     dfd[distilled_columns].rename(columns=rename_columns),
#                     use_container_width=True, hide_index=True)
            

#             if btn_update_d:
#                 dfd_update = dfd_distilled.copy()
#                 dfd_update['remembered'] = False
#                 page_section_update_d: PageSection = build_page_section_with_sentence_list(dataframe=dfd_update,
#                                                             selected_day=page_section_group_d.created_at, 
#                                                             notebook=notebook, 
#                                                             group=page_section_group_d.group,
#                                                             persit=False)
#                 page_section_group_d.translated_sentences  = page_section_update_d.translated_sentences
#                 page_section_update_d.section_number = page_section_group_d.section_number
#                 try:
#                     page_section_dao.update(page_section_update_d)
#                     st.toast('The translation of sentences has been updated!')
#                 except Exception as error:
#                         placeholder_container_msg.error(str(error), icon="🚨")

#             if distill_d and not dfd.empty:
#                 if placehold_container_dt_edit_group_d.button('GROUP D DISTILLATION FINISH', 
#                                                             use_container_width=True, 
#                                                             type='primary', 
#                                                             key='btn_group_d',
#                                                             disabled=True if page_section_group_d.distillated \
#                                                                                 else False):
#                     try:
#                         page_section_update_d: PageSection = build_page_section_with_sentence_list(dataframe=dfd_distilled,
#                                                             selected_day=page_section_group_d.created_at, 
#                                                             notebook=notebook, 
#                                                             group=page_section_group_d.group,
#                                                             persit=False)
#                         page_section_update_d.section_number = page_section_group_d.section_number
#                         page_section_update_d.distillated = True
#                         page_section_dao.update(page_section_update_d)
#                         st.toast('Saving the distillation...')

#                         dfc_base = dfd_distilled[dfd_distilled['remembered'] == False].copy()
#                         dfc_base['translated_sentences'] = ''
#                         page_section_after_d = build_page_section_with_sentence_list(dataframe=dfc_base,
#                                                             selected_day=selected_day, 
#                                                             notebook=notebook, 
#                                                             group=Group.NEW_PAGE,
#                                                             persit=False)
#                         page_section_after_d.set_created_by(page_section_group_d)
#                         page_section_after_d = page_section_dao.insert(page_section_after_d)

#                         st.toast('Distillation was saved!')
#                         placehold_data_edit_group_d.success(f'{page_section_after_d} was inserted successfully!')
#                         notebook.page_section_list.append(page_section_after_d)
#                     except Exception as error:
#                         placeholder_container_msg.error(str(error), icon="🚨")
#                         if 'There is already a page'.upper() in str(error).upper():
#                             st.error(str(error), icon="🚨")
#         else:
#             placehold_data_edit_group_d.warning('⚠️There is no a list of expressions in "Group D" to distill on the selected day!')
    
#     col_group_1.markdown(f'**GroupA:** {notebook.count_page_section_by_group(group=Group.A):0>7}')
#     col_group_2.markdown(f'**GroupB:** {notebook.count_page_section_by_group(group=Group.B):0>7}')
#     col_group_3.markdown(f'**GroupC:** {notebook.count_page_section_by_group(group=Group.C):0>7}')
#     col_group_4.markdown(f'**GroupD:** {notebook.count_page_section_by_group(group=Group.D):0>7}')

else:
    st.warning('⚠️Attention! There are no notebooks registred!')
    st.markdown('[Create a Notebook](Add%20New%20Notebook)')
 