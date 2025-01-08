import streamlit as st
from scripts.ingest_data import (
    fetch_and_send_current_weather,
    fetch_and_send_forecast_weather,
    fetch_and_send_historical_weather,
)

st.set_page_config(page_title="Weather", page_icon="⛅")
st.title('⛅ Weather')


location = st.text_input("Enter City Name or Zip Code", "Brest")
weather_type = st.selectbox("Select Weather Type", ["current", "forecast", "historical"])

if weather_type == "forecast":
    forecast_days = st.slider("Select Number of Days for Forecast", 1, 14, 3)
else:
    forecast_days = None

if weather_type == "historical":
    date = st.date_input("Select Date for Historical Weather")
    hour = st.number_input("Enter Hour (24-hour format)", min_value=0, max_value=23, step=1)
else:
    date, hour = None, None


if st.button("Enter"):
    try:
        if weather_type == "current":
            result = fetch_and_send_current_weather(location)
        elif weather_type == "forecast":
            result = fetch_and_send_forecast_weather(location, forecast_days)
        elif weather_type == "historical":
            result = fetch_and_send_historical_weather(location, date, hour)
        else:
            st.error("Invalid weather type selected.")
            pass

        if result:
            st.success(f"{weather_type.capitalize()} weather data for {location} sent successfully!")
            st.json(result)
        else:
            st.error(f"Failed to fetch {weather_type} weather data for {location}.")
    
    

    except Exception as e:
        st.error(f"Error: {str(e)}")
