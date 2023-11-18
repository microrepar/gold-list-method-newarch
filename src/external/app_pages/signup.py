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
        st.error('\n\n'.join(messages), icon='🚨')
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
        placeholder_error_empty = st.empty()
        
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
            
            error_messages = []
            alert_messages = []            
            username_list = list()
            for index in st.session_state[editor_key]['deleted_rows']:
                
                username = df.iloc[index]['username']                
                if username and 'admin' in username:
                    flag_contem_admin = True
                
                else:
                    user_id = df.iloc[index]['id']
                    username_list.append(username)
                    #############################################################
                    ### DELETE USER BY ID ###
                    #############################################################
                    controller = Controller()
                    request    = {'resource': '/user/delete',
                                'user_id_': user_id}
                    resp       = controller(request=request)
                    #############################################################
                    messages = resp['messages']
                    entities = resp['entities']

                    if messages:
                        error_messages += messages

                    st.write(request)                        
                    st.write(resp)                        
                    #############################################################
                
            if flag_contem_admin:
                alert_messages.append('User "admin" cannot be removed, remove any user except the admin user.')
            
            if error_messages:
                placeholder_error_empty.error('\n\n'.join(error_messages), icon='🚨')
            
            if alert_messages:
                placeholder_alert_empty.warning('\n\n'.join(alert_messages), icon='⚠️')

            st.session_state[editor_key]['deleted_rows'] = []
        
        
        if st.session_state[editor_key].get('edited_rows'):                
            placeholder_alert_empty.error('Changing records via the board is not allowed, please use the form to add new users.', icon='🚨')

        if st.session_state[editor_key].get('added_rows'):
            placeholder_alert_empty.error('Adding new records via the board is not allowed, please use the form to add new users.', icon='🚨')
    
    else:
        st.markdown('### Users')
        st.markdown(':red[Atteption! There are no registred users.]')

else:
    st.warning("Please access **[main page](/)** and enter your username and password.")
