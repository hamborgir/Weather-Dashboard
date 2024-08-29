import streamlit as st
import pandas as pd
from weather import Weather
from datetime import datetime

weather = Weather()

st.title("Weather Forecast Dashboard")

country_res = st.selectbox("Select City", options=weather.get_country_names)

weather_data, utc_offset = weather.fetch_weather_data(country_res)

if weather_data:
    parsed_hourly, parsed_units = Weather.parse_weather_data(weather_data)

    current_utc_time = datetime.utcnow()

    nearest_hour_data = None
    for entry in parsed_hourly:
        entry_utc_time = datetime.fromisoformat(entry['time'])
        if entry_utc_time >= current_utc_time:
            nearest_hour_data = entry
            break

    current_local_time = Weather.get_local_time(current_utc_time.isoformat(), utc_offset)

    st.subheader(f"Weather in {country_res}")

    st.write(f"Current Local Time: {current_local_time}")

    if nearest_hour_data:
        st.write(f"Weather data for the nearest hour ({nearest_hour_data['time']}):")
        st.write(f"Temperature: {nearest_hour_data['temperature_2m']} {parsed_units['temperature_2m']}")
        st.write(f"Relative Humidity: {nearest_hour_data['relative_humidity_2m']} {parsed_units['relative_humidity_2m']}")
        st.write(f"Precipitation Probability: {nearest_hour_data['precipitation_probability']} {parsed_units['precipitation_probability']}")
        st.write(f"Cloud Cover: {nearest_hour_data['cloud_cover']} {parsed_units['cloud_cover']}")
        st.write(f"Visibility: {nearest_hour_data['visibility']} {parsed_units['visibility']}")
        st.write(f"Wind Speed: {nearest_hour_data['wind_speed_10m']} {parsed_units['wind_speed_10m']}")
        st.write(f"UV Index: {nearest_hour_data['uv_index']}")
        st.write(f"Is Day: {'Yes' if nearest_hour_data['is_day'] else 'No'}")
    else:
        st.write("No weather data available for the nearest hour.")
else:
    st.error("Failed to fetch weather data. Please try again later.")
