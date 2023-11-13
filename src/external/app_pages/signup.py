from pathlib import Path

import extra_streamlit_components as stx
import pandas as pd
import streamlit as st  # pip install streamlit
import streamlit_authenticator as stauth  # pip install streamlit-authenticator
import yaml
from st_pages import add_page_title
from yaml.loader import SafeLoader

from src.adapters import Controller

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="Sales Dashboard", page_icon=":bar_chart:", layout="wide")

add_page_title()

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

    try:
        registry = authenticator.register_user('User register', preauthorization=False)

        if registry:
            #############################################################
            ### REGISTRY USER ###
            #############################################################
            username = next(iter(credentials['usernames']))
            controller = Controller()
            request    = {'resource': '/user/registry',
                            'user_username': username,
                            'user_email': credentials['usernames'][username]['email'],
                            'user_name': credentials['usernames'][username]['name'],
                            'user_password': credentials['usernames'][username]['password'],
                        }
            
            resp       = controller(request=request)

            messages = resp['messages']
            entities = resp['entities']

            if messages:
                raise Exception('\n\n'.join(messages))
            #############################################################

            st.success('User registered successfully')       

    except Exception as e:
        st.error(e)


    #############################################################
    ### GET ALL USERS ###
    #############################################################
    controller = Controller()
    request    = {'resource': '/user'}
    resp       = controller(request=request)
    #############################################################
    messages = resp['messages']
    entities = resp['entities']

    if messages:
        st.erro('\n\n'.join(messages), icon='🚨')
    #############################################################

    st.divider()

    if entities:
        st.markdown('### Users')
        df = pd.concat([pd.DataFrame(u.data_to_dataframe()) for u in entities], ignore_index=True)
        placeholder_data_editor = st.empty()

        editor_config = {
            'name': st.column_config.TextColumn('Name (required)', required=True),
            'password': st.column_config.TextColumn('Password'),
            'username': st.column_config.TextColumn('Username'),
            'email': st.column_config.TextColumn('E-mail (required)'),
        }

        if 'flag_reset' not in st.session_state:
            st.session_state.flag_reset = False


        if st.button('Reset', type='primary'):
            st.session_state.flag_reset = not st.session_state.flag_reset
        
        placeholder_alert_empty = st.empty()
        
        if st.session_state.flag_reset:
            editor_key = 'edited_data1'
            edited_df = placeholder_data_editor.data_editor(df, 
                                                        num_rows="dynamic", 
                                                        use_container_width=True,
                                                        column_config=editor_config,
                                                        disabled=['password', 'username'],
                                                        key=editor_key)                
        else:
            editor_key = 'edited_data'
            edited_df = placeholder_data_editor.data_editor(df, 
                                                        num_rows="dynamic", 
                                                        use_container_width=True,
                                                        column_config=editor_config,
                                                        disabled=['password', 'username'],
                                                        key=editor_key)
        
        if st.session_state[editor_key].get('deleted_rows'):  
            
            flag_contem_admin = False
            
            user_id_list = list
            for index in st.session_state[editor_key]['deleted_rows']:
                user_id_list.append(df.iloc[index]['id'])
                username = df.iloc[index]['username']

                if 'admin' in username:
                    flag_contem_admin = True
                    break

            if not flag_contem_admin:
                ...
                # with config_file.open('w') as file:
                #     yaml.dump(config, file, default_flow_style=False)                    
            else:
                placeholder_alert_empty.error('O usuário "admin" não pode ser removido, efetue o reset e exclua qualquer registro de usuário exceto o admin.')
                st.session_state[editor_key]['deleted_rows'] = []
        
        
        if st.session_state[editor_key].get('edited_rows'):                
            placeholder_alert_empty.error('Não é permitido a alteração de registros pelo quadro, por favor use o formulário para adicionar novos usuários.', icon='🚨')
            # try:
            #     with config_file.open('w') as file:
            #         yaml.dump(config, file, default_flow_style=False)                    
                
            #     placeholder_alert_empty.success('Atualização aplicada com sucesso')
            #     st.session_state[editor_key]['edited_rows'] = {}
            # except Exception as error:
            #     placeholder_alert_empty.error(str(error), icon='🚨')

        if st.session_state[editor_key].get('added_rows'):
            placeholder_alert_empty.error('Não é permitido a adição de novos registros pelo quadro, por favor use o formulário para adicionar novos usuários.', icon='🚨')
    


    else:
        st.markdown('### Users')
        st.markdown(':red[Atteption! There are no registred users.]')


else:
    st.warning("Please access **[main page](/)** and enter your username and password.")