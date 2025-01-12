import streamlit as st
from scripts.get_batch_data import (
    define_settings,
    get_data,
    train_test_csv
)

st.set_page_config(page_title="Weather", page_icon="⛅")
st.title('⛅ Weather')

if st.button("Enter"):
    try:
        train_start_date, train_end_date, output_csv_path = define_settings()
        get_data(train_start_date, train_end_date, output_csv_path)
        train_test_csv(output_csv_path)
    except Exception as e:
        st.error(f"Error: {str(e)}")
