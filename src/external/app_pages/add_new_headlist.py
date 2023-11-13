import contextlib
import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth  # pip install streamlit-authenticator
import yaml
from st_pages import add_page_title
from yaml.loader import SafeLoader

from src.adapters import Controller
from src.core.notebook import Notebook
from src.core.pagesection import Group

st.set_page_config(layout='wide')


placeholder_empty_msg = st.empty()
controller = Controller()

# Either this or add_indentation() MUST be called on each page in your
# app to add indendation in the sidebar
add_page_title()  # Optional method to add title and icon to current page

config_file = Path(__file__).parent / 'config.yaml'
with config_file.open('rb') as file:
    config = yaml.load(file, Loader=SafeLoader)

credentials = {'usernames': {}}
config['credentials'] = credentials

authenticator = stauth.Authenticate(
    config['credentials'],              # credentials:      Dict['usernames', Dict['<alias>', Dict['email | name | password', str]]]
    config['cookie']['name'],           # cookie:           str
    config['cookie']['key'],            # cookie:           str
    config['cookie']['expiry_days'],    # cookie:           str
    config['preauthorized'],            # preauthorized:    List[str]
)

st.session_state['username'] = st.session_state['username']

if st.session_state.username:
    # ---- SIDEBAR ----
    authenticator.logout(f"Logout | {st.session_state.username}", "sidebar")

    ######################################################
    # FIND BY FIELD - USER
    ######################################################
    request = {
        'resource': '/user/find_by_field',
        'user_username': st.session_state.username
    }
    resp = controller(request=request)
    messages = resp['messages']
    entities = resp['entities']

    if messages:
        placeholder_empty_msg.error('\n\n'.join(messages), icon='🚨')
        user_id = None
    else:
        user_id = entities[-1].id
    ######################################################


    ######################################################
    # FIND BY FIELD - USER
    ######################################################
    request = {
        'resource': '/notebook/find_by_field',
        'notebook_user': {'user_id_': user_id}
    }
    resp = controller(request=request)
    notebook_list = resp.get('entities')
    messages = resp.get('messages')
    ######################################################


    notebook_dict = {n.name: n for n in notebook_list}

    if not messages:
        selected_notebook = st.sidebar.selectbox('**NOTEBOOK:**', 
                                                notebook_dict.keys())
        
        notebook: Notebook = notebook_dict.get(selected_notebook)
    
        st.subheader(f'{notebook.name.upper()} NOTEBOOK')
        col_group_1, col_group_2, col_group_3, col_group_4 = st.sidebar.columns(4)

        st.sidebar.divider()

        selected_day = st.sidebar.date_input('**LIST OF THE DAY:**', datetime.datetime.now().date(), format='DD/MM/YYYY')
        
        page_section_dict = {p.created_at: p for p in notebook.page_section_list}
        selected_page_section_day = page_section_dict.get(selected_day)

        new_data_add = []    

        if selected_page_section_day is None:
            #############################################################
            ### FIND SENTENCES BY NP GROUP
            #############################################################
            request = {
                'resource': 'pagesection/get_sentences_by_group',
                'pagesection_group': Group.NEW_PAGE,
                'pagesection_notebook': {'notebook_id_': notebook.id},
            }

            resp = controller(request=request)
            sentence_list = resp.get('entities')
            messages = resp.get('messages')

            if messages:
                with placeholder_empty_msg.container():                    
                    for msg in messages:
                        st.info(msg, icon="ℹ️")            
            elif sentence_list:
                placeholder_empty_msg.info(f'{len(sentence_list)} sentences were added to table bellow and are free to compose a new headlist.', icon="ℹ️")
            #############################################################

        for i in range(1, notebook.list_size + 1 ):
            
            sentence_foregin_str = ''
            sentence_mother_str = ''

            with contextlib.suppress(Exception):
                sentence_foregin_str = sentence_list[i-1].foreign_language
                sentence_mother_str = sentence_list[i-1].mother_tongue
                    
                        
            new_data_add.append(
                {
                    "foreign_language": sentence_foregin_str,
                    "mother_tongue": sentence_mother_str
                }
            )

        df_edit = pd.DataFrame(new_data_add)

        column_configuration_data = {
            "foreign_language": st.column_config.TextColumn(
                "Foreign Language", help="The sentece or word that you want to learn",
                required=True
            ),
            "mother_tongue": st.column_config.TextColumn(
                "Mother Tongue", help="translation the sentece or word that you want to learn",
                required=True
            ),
        }

        column_configuration_added = {
            "list_seq": st.column_config.TextColumn(
                "Sequence", help="List Number",
                
            ),
            "date": st.column_config.TextColumn(
                "Created At", help="Insert Date"
            ),
        }

        st.markdown('**Add new HeadList**')

        placeholder_sentences_sheet = st.empty()
        placehold_btn_insert = st.empty()
        placehold_page_exists = st.empty()


        df_result = placeholder_sentences_sheet.data_editor(
            df_edit,
            column_config=column_configuration_data,
            num_rows="fixed",
            hide_index=True,
            use_container_width=True,
        )

        df_result['remembered'] = False
        df_result['translated_sentences'] = ''
        df_result['foreign_idiom'] = notebook.foreign_idiom
        df_result['mother_idiom'] = notebook.mother_idiom
        df_result['created_at'] = selected_day
    

        if selected_page_section_day is not None:
            placeholder_sentences_sheet.warning(f'⚠️There is already a page for the group '
                                                f'{selected_page_section_day.group.value} '
                                                f'and selected day ({selected_page_section_day.created_at}).')
            
        if placehold_btn_insert.button('INSERT NEW LIST', 
                                    type='primary', 
                                    disabled=False if selected_page_section_day is None else True, 
                                    use_container_width=True):

            cols_to_rename = {
                "foreign_language":"sentence_foreign_language",
                "mother_tongue":"sentence_mother_tongue",
                "foreign_idiom":"sentence_foreign_idiom",
                "mother_idiom":"sentence_mother_idiom",
                "created_at":"sentence_created_at",
            }
            df_result.rename(columns=cols_to_rename, inplace=True)

            ###############################################################
            # INSERT PAGESECTION - BODY REQUEST
            ###############################################################
            request = {
                'resource'                         : '/pagesection/registry',
                'pagesection_notebook'             : {'notebook_id_': notebook.id,
                'notebook_days_period'             :   notebook.days_period},
                'pagesection_group'                : Group.HEADLIST,
                'pagesection_created_at'           : selected_day,
                'pagesection_translated_sentences' : df_result['translated_sentences'].to_list(),
                'pagesection_memorializeds'        : df_result['remembered'].to_list(),
                'pagesection_sentences'            : list(df_result.T.to_dict().values()),
            }

            # FrontController
            resp = controller(request=request)
            messages = resp.get('messages')
            entities = resp.get('entities')

            # FeedBack
            if messages:
                with placeholder_empty_msg.container():                    
                    for msg in messages:
                        st.error(msg, icon="🚨")

                st.toast('Something went wrong!')
            elif entities:
                notebook.page_section_list.extend(entities)
                placeholder_sentences_sheet.success(f'{entities[-1]} was inserted successfully!')
                placeholder_empty_msg.success(f'{entities[-1]} was inserted successfully!')
                placehold_btn_insert.empty()
                st.toast('Page section was inserted successfully.')

            # ###############################################################
            # # GET BY ID - NOTEBOOK - BODY REQUEST
            # ###############################################################
            # request = {
            #     'resource': '/notebook/id',
            #     'notebook_id_': notebook.id,
            # }

            # resp = controller(request=request)
            # messages = resp.get('messages')
            # entities = resp.get('entities')

            # # FeedBack
            # if messages:
            #    with placeholder_empty_msg.container():                    
                    # for msg in messages:
                    #     st.error(msg, icon="🚨")
        #         st.toast('Something went wrong!')
            # else:
            #     notebook = entities[-1]        

            # ###############################################################

        qty_group_a = notebook.count_page_section_by_group(group= Group.A)
        qty_group_b = notebook.count_page_section_by_group(group= Group.B)
        qty_group_c = notebook.count_page_section_by_group(group= Group.C)
        qty_group_d = notebook.count_page_section_by_group(group= Group.D)
        
        col_group_1.markdown(f'**GroupA:** {qty_group_a:0>7}')
        col_group_2.markdown(f'**GroupB:** {qty_group_b:0>7}')
        col_group_3.markdown(f'**GroupC:** {qty_group_c:0>7}')
        col_group_4.markdown(f'**GroupD:** {qty_group_d:0>7}')

        st.divider()

        if notebook.page_section_list:
            df = pd.concat([pd.DataFrame(n.data_to_dataframe()) for n in notebook.page_section_list \
                            if n.group == Group.A and n.created_at != n.distillation_at], ignore_index=True)
            df = df.groupby('created_at').first().reset_index()
            df_result = df.sort_values('created_at', ascending=False).head(5)

            columns = ['created_at', 'id', 'page_number', 'group', 'distillation_at', 'distillation_actual', 'notebook_id']

            st.markdown('#### Last 5 Registred HeadLists:')
            st.dataframe(df_result[columns], hide_index=True, use_container_width=True)
            st.markdown(f'Lines total: {df.shape[0]}')
        else:
            st.subheader('HeadLists')
            st.markdown(':red[Atteption! There are no registred Headlists.]')

    else:
        st.warning('⚠️Attention! There are no notebooks registred!')
        st.markdown('[Create a Notebook](Add%20Notebook)')
else:
    st.warning("Please access **[main page](/)** and enter your username and password.")