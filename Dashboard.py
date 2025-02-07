import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import io
import io
import plotly.express as px
import plotly.graph_objects as go

st. set_page_config(layout="wide")

# Ensure session state is initialized for uploaded CSV and DataFrame
if 'uploaded_csv' not in st.session_state:
    st.session_state.uploaded_csv = None
if 'df' not in st.session_state:
    st.session_state.df = None





# Define menu with option_menu
# selected = option_menu(
#     menu_title=None,
#     options=["Home", "Charts", "Columns"],
#     icons=["house", "graph-up", "columns"],
#     menu_icon="cast",
#     default_index=0,
    
# )




# Home tab - Upload CSV and store DataFrame

st.markdown("<h1 style='text-align: center;'>Dashboard</h1>", unsafe_allow_html=True)
st.markdown("---")

uploaded_file = st.file_uploader("Upload Your CSV", type=["csv"])

if uploaded_file is not None:
    st.session_state.uploaded_csv = uploaded_file
    csv_data = uploaded_file.getvalue()
    st.session_state.df = pd.read_csv(io.BytesIO(csv_data))

if st.session_state.df is not None:
    df = st.session_state.df

    if df.empty:
        st.warning("The uploaded CSV file is empty. Please upload a valid file.")
    else:
        edited_df = st.data_editor(df, use_container_width=True, hide_index=True)
        # edited_df['random_date_formatted'] = pd.to_datetime(df['random_date']).dt.strftime('%b %d, %Y')
        csv_bytes = edited_df.to_csv(index=False).encode('utf-8')

        st.download_button(
            label='Download Edited CSV',
            data=csv_bytes,
            file_name='edited_data.csv',
            mime='text/csv'
        )
else:
    st.info("Please upload a CSV file to continue.")

