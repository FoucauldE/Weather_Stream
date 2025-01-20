import streamlit as st

st.set_page_config(page_title="Rainfall", page_icon="🌧️")
st.title("Welcome back ! ☀️")

st.markdown(
    """
    ### Forecasting and Analysing Rainfall 🌧️

    This platform is dedicated to helping solar panel users optimize energy production by providing precise cloud cover information and forecasts.

    **What you can do:**
    1. **⛅ Consult weather**: View real-time weather insights for any location on the globe. 🌍
    2. **⚙️ Train a static model**: Download past data and train/test your own static model to predict the rain. 🌧️
    3. **🔮 Access Predictions**: Explore forecasts for rainfall in the coming hour and compare the results with other models. 🔋

    **Why this is useful:**
    - Stay informed about upcoming weather changes.
    - Compare performance between static and online models.
    - Propose a complete pipeline to predict rainfall.

    Ready to get started? Navigate to one of the pages using the menu on the left! ✔️
    """
)

st.markdown(
    """
    ---
    🌍 **Powered by [WeatherAPI](https://www.weatherapi.com/)** | Developed by the cooks.
    """,
    unsafe_allow_html=True
)