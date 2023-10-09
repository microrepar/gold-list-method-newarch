import datetime

import pandas as pd
import streamlit as st
from st_pages import add_page_title

from src.adapters import Controller

controller = Controller()

st.set_page_config(layout='wide')

# Either this or add_indentation() MUST be called on each page in your
# app to add indendation in the sidebar
placehold_msg = st.empty()

with placehold_msg:
    placehold_msg_container = st.container()

add_page_title()
 
# st.title('NEW NOTEBOOK')

with st.form("my_form"):   
    st.write("Create Notebook")
    notebook_name = st.text_input('Notebook name')
    col1, col2 = st.columns(2)
    foreign_idiom = col1.text_input('Foreign idiom')
    mother_idiom = col2.text_input('Mother idiom')
    col1, col2 = st.columns(2)
    list_size = col1.slider("List size", min_value=10, max_value=25, value=20)
    days_period = col2.slider("Days period", min_value=5, max_value=20, value=15)

    # Every form must have a submit button.
    submitted = st.form_submit_button("ADD NEW NOTEBOOK", type="primary", use_container_width=True)

if submitted:
    request = {
        'resource': '/notebook/registry',
        'notebook_name': notebook_name,
        'notebook_created_at': datetime.datetime.now().date(),
        'notebook_list_size': list_size,
        'notebook_days_period': days_period,
        'notebook_foreign_idiom': foreign_idiom,
        'notebook_mother_idiom': mother_idiom,
    }

    resp = controller(request=request)

    msg = resp.get('messages')
    
    if msg:
        for msg in resp.get('messages'):
            placehold_msg_container.error(str(msg), icon="🚨")
        else:
            st.toast('Something went wrong!')
    else:
        new_notebook = resp.get('entities', [None])[-1]
        placehold_msg_container.success(f'{new_notebook} was inserted successfully!')
        st.toast('Notebook was inserted successfully.')


request = {
    'resource': '/notebook'
}
resp = controller(request)

notebook_list = resp.get('entities')
if notebook_list:
    df = pd.concat([pd.DataFrame(n.data_to_dataframe()) for n in notebook_list], ignore_index=True)
    st.subheader('Notebooks')
    st.dataframe(df, hide_index=True, use_container_width=True)
else:
    st.subheader('Notebooks')
    st.markdown(':red[Atteption! There are no registred notebooks.]')
