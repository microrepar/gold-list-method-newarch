import datetime

import pandas as pd
import streamlit as st
from st_pages import add_page_title

from src.adapters import Controller
from src.core.notebook import Notebook
from src.core.pagesection import Group

st.set_page_config(layout='wide')

placeholder_container_msg = st.container()
placeholder_container_msg.empty()

# Either this or add_indentation() MUST be called on each page in your
# app to add indendation in the sidebar
add_page_title()  # Optional method to add title and icon to current page


#############################################################
controller = Controller()
request = {
    'resource': '/notebook'
}
resp = controller(request=request)
notebook_list = resp.get('entities')
messages = resp.get('messages')
#############################################################


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

    sentences_txt = [("I love learning new languages.", "Eu adoro aprender novos idiomas."), ("She enjoys reading books in her free time.", "Ela gosta de ler livros nas horas vagas."), ("They went to the beach last weekend.", "Eles foram à praia no fim de semana passado."), ("I'm going to the grocery store to buy some groceries.", "Vou à mercearia comprar mantimentos."), ("He is a talented musician who plays the guitar beautifully.", "Ele é um músico talentoso que toca violão lindamente."), ("She usually takes a walk in the park after dinner.", "Normalmente, ela dá uma caminhada no parque depois do jantar."), ("I can't wait to see you again.", "Mal posso esperar para te ver de novo."), ("My favorite movie is a classic from the 80s.", "Meu filme favorito é um clássico dos anos 80."), ("They are planning a family vacation to Europe next summer.", "Eles estão planejando uma viagem em família para a Europa no próximo verão."), ("The weather is very hot today.", "O clima está muito quente hoje."), ("I need to study for my exams this weekend.", "Preciso estudar para as provas neste fim de semana."), ("She's a great cook and makes delicious meals.", "Ela é uma ótima cozinheira e faz refeições deliciosas."), ("He's always telling funny jokes that make everyone laugh.", "Ele está sempre contando piadas engraçadas que fazem todos rirem."), ("I enjoy going for a run in the morning.", "Gosto de sair para correr de manhã."), ("They are planning a surprise party for her birthday.", "Eles estão planejando uma festa surpresa para o aniversário dela."), ("She wants to travel the world and explore different cultures.", "Ela quer viajar pelo mundo e explorar diferentes culturas."), ("I have a lot of work to do this week.", "Tenho muito trabalho para fazer esta semana."), ("We had a great time at the concert last night.", "Nos divertimos muito no show de ontem à noite."), ("He's an excellent student and always gets good grades.", "Ele é um ótimo aluno e sempre tira boas notas."), ("They are going to visit their grandparents during the holidays.", "Eles vão visitar os avós durante as férias.")]
    new_data_add = []
    for i in range(1, notebook.list_size + 1 ):
        new_data_add.append(
            {
                "foreign_language": sentences_txt[i-1][0],
                "mother_tongue": sentences_txt[i-1][1],
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
            for msg in messages:
                placeholder_container_msg.error(msg,  icon="🚨")
                st.toast('Something went wrong!')
        elif entities:
            notebook.page_section_list.extend(entities)
            placeholder_sentences_sheet.success(f'{entities[-1]} was inserted successfully!')
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
        #     for msg in messages:
        #         placeholder_container_msg.error(msg,  icon="🚨")
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





