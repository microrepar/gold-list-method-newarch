import pickle
from pathlib import Path

import streamlit as st  # pip install streamlit
import streamlit_authenticator as stauth  # pip install streamlit-authenticator
import yaml
from st_pages import add_page_title
from yaml.loader import SafeLoader

import extra_streamlit_components as stx

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

else:
    st.warning("Please access **[main page](/)** and enter your username and password.")