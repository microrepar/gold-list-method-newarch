from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
import streamlit as st
from st_pages import show_pages_from_config, add_page_title

st.set_page_config(layout='wide')

# Either this or add_indentation() MUST be called on each page in your
# app to add indendation in the sidebar
add_page_title()


# st.title('SET CONFIGURATION')

selected_notebook = st.sidebar.selectbox('Notebook:', ['Gold List 2023', 'Silver List 2023'])

with st.form("my_form"):
   
   st.write("Set configuration")
   col1, col2 = st.columns(2)
   notebook_name = st.text_input('Notebook name', value=selected_notebook)
   slider_val = st.slider("List size", min_value=10, max_value=25, value=20)

   # Every form must have a submit button.
   submitted = st.form_submit_button("Submit", type="primary", use_container_width=True)
   if submitted:
       st.write("slider", slider_val, "checkbox")
