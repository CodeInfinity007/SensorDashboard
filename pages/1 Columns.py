import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import io
# from mpld3 import plugins
import io
import plotly.express as px
import plotly.graph_objects as go


# Columns tab

st.markdown("<h1 style='text-align: center;'>Columns</h1>", unsafe_allow_html=True)
st.markdown("---")

if st.session_state.df is not None:
    data = st.session_state.df
    r1col1, r1col2 = st.columns(2)
    with r1col1:
        st.write("DataFrame Preview:")
        st.write(st.session_state.df)

    with r1col2:
        st.write("Line Chart: ")
        st.session_state.line_x = st.selectbox("X Axis: ", data.columns, index=data.columns.get_loc(st.session_state.get('line_x', data.columns[0])), key='x_axis1')
        st.session_state.line_y = st.selectbox("Y Axis: ", data.columns, index=data.columns.get_loc(st.session_state.get('line_y', data.columns[0])), key='y_axis1')

        st.markdown("#")
        st.write("Bar Graph")
        st.session_state.bar_x = st.selectbox("X Axis: ", data.columns, index=data.columns.get_loc(st.session_state.get('bar_x', data.columns[0])), key='x_axis2')
        st.session_state.bar_y = st.selectbox("Y Axis: ", data.columns, index=data.columns.get_loc(st.session_state.get('bar_y', data.columns[0])), key='y_axis2')

    r2c1, r2c2, r2c3 = st.columns(3)

    with r2c1:
          
        st.write("Pie Chart: ")
        st.session_state.pie_vals = st.selectbox("Values to show: ", data.columns, index=data.columns.get_loc(st.session_state.get('pie_vals', data.columns[0])), key='pie_vals1')
        st.session_state.pie_factor_columns = st.selectbox("Factor: ", data.columns, index=data.columns.get_loc(st.session_state.get('pie_factor_columns', data.columns[0])), key='pie_factor_1')
        
    
    with r2c2:
            
        pass
    with r2c3:
        pass
        

else:
    st.info("Upload a CSV file and switch back to see columns.")

