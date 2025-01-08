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
    forecast_days = st.selectbox("Select Number of Days for Forecast", [i for i in range(1, 4)])
    forecast_hours = st.number_input("Enter the hour for Forecast (for the 'Per hour section') (24-hour format)", min_value=0, max_value=23, step=1)
else:
    forecast_days = None
    forecast_hours = None

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

            if weather_type == "current":
                # Sections
                tab1, tab2, tab3 = st.tabs(["General summary", "Detailed conditions", "Wind and visibility"])

                # General summary
                with tab1:
                    st.header("General summary")
                    st.metric("Temperature (°C)", f"{result['temp_c']} °C")
                    st.metric("Temperature (°F)", f"{result['temp_f']} °F")
                    st.metric("Last update", result["last_updated"])
                    st.image("https:" + result["condition"]["icon"], caption=result["condition"]["text"])
                
                # Detailed conditions
                with tab2:
                    st.header("Detailed conditions")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("### Pressure and Precipitation")
                        st.metric("Pressure (mb)", f"{result['pressure_mb']} mb")
                        st.metric("Precipitation (mm)", f"{result['precip_mm']} mm")
                        st.metric("Humidity (%)", f"{result['humidity']} %")
                    with col2:
                        st.write("### Comfort data")
                        st.metric("Feelslike (°C)", f"{result['feelslike_c']} °C")
                        st.metric("Dewpoint (°C)", f"{result['dewpoint_c']} °C")
                        st.metric("UV index", f"{result['uv']}")

                # Wind and visibility
                with tab3:
                    st.header("Wind and Visibility")
                    st.metric("Wind velocity (km/h)", f"{result['wind_kph']} km/h")
                    st.metric("Wind direction", f"{result['wind_dir']} ({result['wind_degree']}°)")
                    st.metric("Visibility (km)", f"{result['vis_km']} km")
                    st.metric("Gusts (km/h)", f"{result['gust_kph']} km/h")
            
            elif weather_type == "forecast":
                # Sections
                tab1, tab2, tab3 = st.tabs(["Day info", "Astronomy", "Per hour"])
                day = result["forecastday"][forecast_days-1]["day"]

                # Day info
                with tab1:
                    st.header("Day info")

                    # Section "General condition"
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image("https:" + day["condition"]["icon"], caption=day["condition"]["text"])
                    with col2:
                        st.metric("Average temperature (°C)", f"{day['avgtemp_c']} °C")
                        st.metric("Average temperature (°F)", f"{day['avgtemp_f']} °F")
                        st.metric("Average humidity (%)", f"{day['avghumidity']} %")
                        st.metric("UV index", f"{day['uv']}")

                    # Section "Temperatures"
                    st.divider()
                    st.header("Temperatures")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Max Temperature (°C)", f"{day['maxtemp_c']} °C")
                        st.metric("Min Température (°C)", f"{day['mintemp_c']} °C")
                    with col2:
                        st.metric("Max Temperature (°F)", f"{day['maxtemp_f']} °F")
                        st.metric("Min Temperature (°F)", f"{day['mintemp_f']} °F")

                    # Section "Wind and precipitations"
                    st.divider()
                    st.header("Wind and precipitations")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total precipitations (mm)", f"{day['totalprecip_mm']} mm")
                        st.metric("Total precipitations (in)", f"{day['totalprecip_in']} in")
                        st.metric("Total snow (cm)", f"{day['totalsnow_cm']} cm")
                        st.metric("Average visibility (km)", f"{day['avgvis_km']} km")
                    with col2:
                        st.metric("Max wind speed (km/h)", f"{day['maxwind_kph']} km/h")
                        st.metric("Max wind speed (mph)", f"{day['maxwind_mph']} mph")
                        st.metric("Rain probability (%)", f"{day['daily_chance_of_rain']} %")
                        st.metric("Snow probability (%)", f"{day['daily_chance_of_snow']} %")
                    # Astro
                    with tab2:
                        st.header("Astronomical Data")
                        astro = result["forecastday"][forecast_days-1]["astro"]

                        # Section: Sun information
                        st.header("☀️ Sun Information")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Sunrise", astro["sunrise"])
                        with col2:
                            st.metric("Sunset", astro["sunset"])

                        # Divider for visual separation
                        st.divider()

                        # Section: Moon information
                        st.header("🌕 Moon Information")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Moonrise", astro["moonrise"])
                            st.metric("Moonset", astro["moonset"])
                        with col2:
                            st.metric("Moon Illumination (%)", f"{astro['moon_illumination']}%")
                            st.metric("Moon Phase", astro["moon_phase"])

                    # Per hour
                    with tab3:
                        st.header("Per hour")
                        per_hour = result["forecastday"][forecast_days-1]["hour"][forecast_hours]

                        # Section: General Information
                        st.header("🌡️ General Information")
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            st.image("https:" + per_hour["condition"]["icon"], caption=per_hour["condition"]["text"])
                        with col2:
                            st.metric("Temperature (°C)", f"{per_hour['temp_c']} °C")
                            st.metric("Temperature (°F)", f"{per_hour['temp_f']} °F")
                            st.metric("Feels Like (°C)", f"{per_hour['feelslike_c']} °C")
                            st.metric("Humidity (%)", f"{per_hour['humidity']}%")

                        # Section: Wind Information
                        st.divider()
                        st.header("💨 Wind and Visibility")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Wind Speed (km/h)", f"{per_hour['wind_kph']} km/h")
                            st.metric("Wind Speed (mph)", f"{per_hour['wind_mph']} mph")
                            #st.metric("Wind Direction", f"{per_hour['wind_dir']} ({per_hour['wind_degree']}°)")
                            #st.metric("Gust Speed (km/h)", f"{per_hour['gust_kph']} km/h")
                        with col2:
                            st.metric("Visibility (km)", f"{per_hour['vis_km']} km")
                            st.metric("Visibility (miles)", f"{per_hour['vis_miles']} miles")
                            st.metric("Cloud Coverage (%)", f"{per_hour['cloud']}%")

                        # Section: Precipitation and Pressure
                        st.divider()
                        st.header("🌧️ Precipitation and Pressure")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Precipitation (mm)", f"{per_hour['precip_mm']} mm")
                            st.metric("Precipitation (in)", f"{per_hour['precip_in']} in")
                            st.metric("Chance of Rain (%)", f"{per_hour['chance_of_rain']}%")
                            st.metric("Chance of Snow (%)", f"{per_hour['chance_of_snow']}%")
                        with col2:
                            st.metric("Pressure (mb)", f"{per_hour['pressure_mb']} mb")
                            st.metric("Pressure (in)", f"{per_hour['pressure_in']} in")
                            st.metric("Snow (cm)", f"{per_hour['snow_cm']} cm")

                        # Section: Additional Information
                        st.divider()
                        st.header("📜 Additional Information")
                        st.metric("Heat Index (°C)", f"{per_hour['heatindex_c']} °C")
                        st.metric("Heat Index (°F)", f"{per_hour['heatindex_f']} °F")
                        st.metric("Dew Point (°C)", f"{per_hour['dewpoint_c']} °C")
                        st.metric("Dew Point (°F)", f"{per_hour['dewpoint_f']} °F")
                        st.metric("UV Index", f"{per_hour['uv']}")
            elif weather_type == "historical":
                # Sections
                day = result["forecastday"][0]["day"]
                date = result["forecastday"][0]["date"]
                st.metric("Date", date)
                tab1, tab2, tab3 = st.tabs(["Day info", "Astronomy", "Targeted hour"])

                # Day info
                with tab1:
                    st.header("Day info")

                    # Section "General condition"
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image("https:" + day["condition"]["icon"], caption=day["condition"]["text"])
                    with col2:
                        st.metric("Average temperature (°C)", f"{day['avgtemp_c']} °C")
                        st.metric("Average temperature (°F)", f"{day['avgtemp_f']} °F")
                        st.metric("Average humidity (%)", f"{day['avghumidity']} %")
                        st.metric("UV index", f"{day['uv']}")

                    # Section "Temperatures"
                    st.divider()
                    st.header("Temperatures")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Max Temperature (°C)", f"{day['maxtemp_c']} °C")
                        st.metric("Min Température (°C)", f"{day['mintemp_c']} °C")
                    with col2:
                        st.metric("Max Temperature (°F)", f"{day['maxtemp_f']} °F")
                        st.metric("Min Temperature (°F)", f"{day['mintemp_f']} °F")

                    # Section "Wind and precipitations"
                    st.divider()
                    st.header("Wind and precipitations")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total precipitations (mm)", f"{day['totalprecip_mm']} mm")
                        st.metric("Total precipitations (in)", f"{day['totalprecip_in']} in")
                        st.metric("Total snow (cm)", f"{day['totalsnow_cm']} cm")
                        st.metric("Average visibility (km)", f"{day['avgvis_km']} km")
                    with col2:
                        st.metric("Max wind speed (km/h)", f"{day['maxwind_kph']} km/h")
                        st.metric("Max wind speed (mph)", f"{day['maxwind_mph']} mph")
                        st.metric("Rain probability (%)", f"{day['daily_chance_of_rain']} %")
                        st.metric("Snow probability (%)", f"{day['daily_chance_of_snow']} %")
                    # Astro
                    with tab2:
                        st.header("☀️ Astronomical Data 🌕")
                        astro = result["forecastday"][0]["astro"]

                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Sunrise", astro["sunrise"])
                            st.metric("Sunset", astro["sunset"])
                        with col2:
                            st.metric("Moonrise", astro["moonrise"])
                            st.metric("Moonset", astro["moonset"])
                            st.metric("Moon Phase", astro["moon_phase"])
                            st.metric("Moon Illumination (%)", f"{astro['moon_illumination']}%")

                    # Per hour
                    with tab3:
                        st.header("Per hour")
                        per_hour = result["forecastday"][0]["hour"][0]
                        hour = per_hour["time"]
                        st.metric("Hour", hour)
                        # Section: General Information
                        st.header("🌡️ General Information")
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            st.image("https:" + per_hour["condition"]["icon"], caption=per_hour["condition"]["text"])
                        with col2:
                            st.metric("Temperature (°C)", f"{per_hour['temp_c']} °C")
                            st.metric("Temperature (°F)", f"{per_hour['temp_f']} °F")
                            st.metric("Feels Like (°C)", f"{per_hour['feelslike_c']} °C")
                            st.metric("Humidity (%)", f"{per_hour['humidity']}%")

                        # Section: Wind Information
                        st.divider()
                        st.header("💨 Wind and Visibility")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Wind Speed (km/h)", f"{per_hour['wind_kph']} km/h")
                            st.metric("Wind Speed (mph)", f"{per_hour['wind_mph']} mph")
                            #st.metric("Wind Direction", f"{per_hour['wind_dir']} ({per_hour['wind_degree']}°)")
                            #st.metric("Gust Speed (km/h)", f"{per_hour['gust_kph']} km/h")
                        with col2:
                            st.metric("Visibility (km)", f"{per_hour['vis_km']} km")
                            st.metric("Visibility (miles)", f"{per_hour['vis_miles']} miles")
                            st.metric("Cloud Coverage (%)", f"{per_hour['cloud']}%")

                        # Section: Precipitation and Pressure
                        st.divider()
                        st.header("🌧️ Precipitation and Pressure")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Precipitation (mm)", f"{per_hour['precip_mm']} mm")
                            st.metric("Precipitation (in)", f"{per_hour['precip_in']} in")
                            st.metric("Chance of Rain (%)", f"{per_hour['chance_of_rain']}%")
                            st.metric("Chance of Snow (%)", f"{per_hour['chance_of_snow']}%")
                        with col2:
                            st.metric("Pressure (mb)", f"{per_hour['pressure_mb']} mb")
                            st.metric("Pressure (in)", f"{per_hour['pressure_in']} in")
                            st.metric("Snow (cm)", f"{per_hour['snow_cm']} cm")

                        # Section: Additional Information
                        st.divider()
                        st.header("📜 Additional Information")
                        st.metric("Heat Index (°C)", f"{per_hour['heatindex_c']} °C")
                        st.metric("Heat Index (°F)", f"{per_hour['heatindex_f']} °F")
                        st.metric("Dew Point (°C)", f"{per_hour['dewpoint_c']} °C")
                        st.metric("Dew Point (°F)", f"{per_hour['dewpoint_f']} °F")
                        st.metric("UV Index", f"{per_hour['uv']}")
                        





            
        else:
            st.error(f"Failed to fetch {weather_type} weather data for {location}.")
    
    

    except Exception as e:
        st.error(f"Error: {str(e)}")
