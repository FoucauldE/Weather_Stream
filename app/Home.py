import streamlit as st

st.set_page_config(page_title="Cloud Cover", page_icon="☁️")
st.title("Welcome back ! ☀️")

st.markdown(
    """
    ### Forecasting and Analysing Cloud Cover ☁️

    This platform is dedicated to helping solar panel users optimize energy production by providing precise cloud cover information and forecasts.

    **What you can do:**
    1. **⛅ Consult Cloud Cover**: View real-time cloud cover data for any location on the globe. 🌍
    2. **🚨 Set Alerts**: Receive live notifications when the cloud cover is low—perfect for maximizing your solar energy production. 🚀
    3. **🔮 Access Predictions**: Explore forecasts for cloud cover in the coming hours to plan your energy strategy. 🔋

    **Why this is useful:**
    - Stay informed about upcoming weather changes.
    - Optimize the use of solar panels to enhance energy efficiency.
    - Receive proactive alerts for better planning and energy management.

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