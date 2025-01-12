import streamlit as st
from scripts.batch_model import main

st.set_page_config(page_title="Weather", page_icon="⛅")
st.title('⛅ Weather')

if st.button("Enter"):
    try:
        R2 = main()
        if R2 is not None:
            st.success(f"Batch model was trained successfully!")
        else:
            st.error(f"Failed to train batch model.")
    except Exception as e:
        st.error(f"Error: {str(e)}")
