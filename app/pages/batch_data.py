import streamlit as st
from scripts.ingest_data import get_past_data, format_csv

st.set_page_config(page_title="Weather", page_icon="⛅")
st.title('⛅ Weather')

if st.button("Enter"):
    try:
        get_past_data(location=None, output_csv_name="past_data_essai.csv")
        format_csv()
    except Exception as e:
        st.error(f"Error: {str(e)}")
