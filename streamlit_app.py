import os
from datetime import date
import pandas as pd
import numpy as np
import streamlit as st
from snowflake.snowpark import Session
from st_aggrid import AgGrid, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder
from collections import Counter
import plotly.graph_objects as go
import plotly.express as px
########################################################################################################################

st.set_page_config(
    page_title="MT",
    page_icon='shark',
    layout='wide')

######################################################################################################################
style_data = os.path.join(os.path.dirname(__file__),'style/styles.css')
with open(style_data) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


############################################################################################################################
try:
    session = st.connection("snowflake")
    status = 'green'
except:
    session =  None
    status = 'red'

@st.cache_data(show_spinner=True)
def get_df():
     df = session.query("SELECT * FROM SCANS")
     cou = session.query("select count(ID) from SCANS")
     feedbacks =  session.query("SELECT count(comments) FROM scans WHERE comments IS NOT NULL;")
     df['IDP']=df['ID'].apply(lambda x: x.split('_')[0])
     scansCount = dict(Counter(df['IDP']))
     scansCount = dict(sorted(scansCount.items(), key=lambda item: item[1], reverse=True))
     return df,cou,feedbacks,scansCount

#############################################################################################################################
    
if 'current_screen' not in st.session_state:
    st.session_state.current_screen = 'screen_one'

with st.sidebar:
    _,c1 =  st.columns([0.05,0.95])
    with c1:
        st.markdown("<h1 style='color:white; text-align: center;'>Menu  ☰</h1>", unsafe_allow_html=True)

        if st.button("Home 🏠",use_container_width=True,):
            st.session_state.current_screen = 'screen_one'
        if st.button("Detect 🔍",use_container_width=True):
            st.session_state.current_screen = 'screen_two'
        


if st.session_state.current_screen == 'screen_one':
    with st.container():
        c1,c2 = st.columns([0.8,0.2])

        with c1: 
            st.write(f"Date: {date.today().strftime('%d/%m/%Y')} ")
        with c2:
            st.markdown(f"<h3 style='color:{status}; text-align: center;'>Hi Groot 🤴</h3>", unsafe_allow_html=True)

    with st.container():

        c1,_,c2 = st.columns([0.6,0.1,0.3])
        
        with c2:
            if session is not None: 
                df,cou,feedbacks,scansCount = get_df()
                search_term =  st.text_input('Search . . .')
                if search_term:
                    tmp_df = df[df['ID'].str.lower().str.contains(search_term.lower())]
                else:
                    tmp_df = df.copy()
                gd = GridOptionsBuilder.from_dataframe(pd.DataFrame(tmp_df.loc[:,'ID']))
                gd.configure_selection(selection_mode='multiple', use_checkbox=True,rowMultiSelectWithClick=True)
                gridoptions = gd.build()

                grid_table = AgGrid(pd.DataFrame(tmp_df.loc[:,'ID']), height=400, gridOptions=gridoptions,
                                    update_mode=GridUpdateMode.SELECTION_CHANGED,columns_auto_size_mode=2)
                if len(grid_table["selected_rows"])>0:
                    selected_x = pd.DataFrame(grid_table["selected_rows"])['ID'].to_list()
                else:
                    selected_x = []
            
            
            else:
                df = None
        
        with c1:
            c11,c12 = st.columns([0.8,0.2])
            with c12:
                if df is not None:
                    opt = st.selectbox('',['XCAL','YCAL','RAW'])
            tmp_df = df[df['ID'].isin(selected_x)]
            
            try:
                tmp_df[opt] = tmp_df[opt].apply(eval).apply(eval)
            except:
                tmp_df[opt] = tmp_df[opt].apply(eval)
            

            fig = go.Figure()
            for _,row in tmp_df.iterrows():
                fig.add_trace(go.Scatter(x=np.arange(200,2601), y=row[opt], mode='lines', name=row['ID']))

            fig.update_layout(
                    title=f"{opt}",
                    xaxis_title="Peaks",
                    showlegend=True,
                    
                )
            st.plotly_chart(fig, use_container_width=True)
            
    st.divider()
    with st.container():
        c1,_,c2 = st.columns([0.6,0.1,0.3])
        with c1:
            with st.container():
                fig = px.bar(x=list(scansCount.keys()), y=list(scansCount.values()), labels={'x': 'Categories', 'y': 'Values'})
                fig.update_layout(title="Scans Count", xaxis_title="Categories", yaxis_title="Values")
                st.plotly_chart(fig)

        with c2:
            with st.container():
                st.metric("Total Scans",cou.values.ravel()[0],'0')
                st.divider()
                st.metric("Feedbacks",feedbacks.values.ravel()[0],'0')

            
                

if st.session_state.current_screen == 'screen_two':
    with st.container():
        c1,c2 = st.columns([0.8,0.2])

        with c1: 
            st.write(f"Date: {date.today().strftime('%d/%m/%Y')} ")
        with c2:
            st.markdown(f"<h3 style='color:{status}; text-align: center;'>Hi Groot 🤴</h3>", unsafe_allow_html=True)

    with st.container():

        c1,c2 = st.columns([0.6,0.4])
        
        with c2:
            if session is not None: 
                df,cou,feedbacks,scansCount = get_df()
                search_term =  st.text_input('Search . . .')
                if search_term:
                    tmp_df = df[df['ID'].str.lower().str.contains(search_term.lower())]
                else:
                    tmp_df = df.copy()
                gd = GridOptionsBuilder.from_dataframe(pd.DataFrame(tmp_df.loc[:,'ID']))
                gd.configure_selection(selection_mode='multiple', use_checkbox=True,rowMultiSelectWithClick=True)
                gridoptions = gd.build()

                grid_table = AgGrid(pd.DataFrame(tmp_df.loc[:,'ID']), height=150, gridOptions=gridoptions,
                                    update_mode=GridUpdateMode.SELECTION_CHANGED,columns_auto_size_mode=2)
                if len(grid_table["selected_rows"])>0:
                    selected_x = pd.DataFrame(grid_table["selected_rows"])['ID'].to_list()
                else:
                    selected_x = []
            
            
            else:
                df = None
        
        with c1:
            c11,c12 = st.columns([0.8,0.2])
            with c12:
                if df is not None:
                    opt = st.selectbox('',['XCAL'])
            tmp_df = df[df['ID'].isin(selected_x)]
            
            try:
                tmp_df[opt] = tmp_df[opt].apply(eval).apply(eval)
            except:
                tmp_df[opt] = tmp_df[opt].apply(eval)
            

            fig = go.Figure()
            for _,row in tmp_df.iterrows():
                fig.add_trace(go.Scatter(x=np.arange(200,2601), y=row[opt], mode='lines', name=row['ID']))

            fig.update_layout(
                    title=f"{opt}",
                    xaxis_title="Peaks",
                    showlegend=True,
                    
                )
            st.plotly_chart(fig, use_container_width=True)
        
    with c2:
        _,c22 = st.columns([0.5,0.5])
        res_df = None
        with c22:
            if st.button('Predict',use_container_width=True):
                if len(selected_x)==1:
                    res_df = session.query(f"""call identify_check('{selected_x[0]}')""")
                    
                else:
                    st.warning("Please Select Single Scan")
        if res_df is not None:
            res_df = eval(res_df.iloc[0,0])
            res = {}
            ids,sc = 'None',0
            for r,s  in res_df.items():
                res[r]=eval(s['percentage'])
                if sc<eval(s['percentage']): sc,ids=eval(s['percentage']),r
            with st.container():
                st.metric("Detected",ids,sc)
                
    
    st.divider()
    with st.container():
        c1,_,c2 = st.columns([0.6,0.1,0.3])
        with c1:
            if res_df is not None:
                fig = px.bar(x=list(res.keys()), y=list(res.values()), labels={'x': 'Substance', 'y': 'score'})
                fig.update_layout(title="Probability", xaxis_title="Substance", yaxis_title="Score")
                st.plotly_chart(fig)