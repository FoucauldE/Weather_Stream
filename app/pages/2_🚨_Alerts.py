import streamlit as st

st.set_page_config(page_title="Alerts", page_icon="🚨")
st.title('🚨 Alerts')

location = st.text_input("Enter City Name or Zip Code", "Brest")
if st.button("Get Alerted"):
    pass