import requests
from config.config import API_URL
from config.private_config import API_KEY
from helper.tools import preprocess_data

def get_weather_data(endpoint, params):
    """Generic function to make requests to the WeatherAPI."""
    try:
        params['key'] = API_KEY
        url = f"{API_URL}/{endpoint}.json"
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching data from WeatherAPI: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"Error fetching weather data: {str(e)}")
        return None


def get_current_weather(location):
    """Fetch current weather for a given location."""
    params = {'q': location}
    data = get_weather_data('current', params)
    if data and 'current' in data:
        data_weather = data.get('current')
        lat, lon = data.get('location')['lat'], data.get('location')['lon']
        data_weather['lat'], data_weather['lon'] = lat, lon
        return data_weather
    else:
        return None


def get_forecast_weather(location, days):
    """Fetch weather forecast for a given location and number of days."""
    if days < 1 or days > 14:
        print("Forecast days must be between 1 and 14.")
        return None
    
    params = {'q': location, 'days': days}
    data = get_weather_data('forecast', params)
    if data:
        return data.get('forecast')
    return None


def get_historical_weather(location, date, hour=None):
    """Fetch historical weather for a given location and date."""
    params = {'q': location, 'dt': date}
    if hour:
        params['hour'] = hour
    
    data = get_weather_data('history', params)
    data_weather = data.get('forecast')
    lat, lon = data.get('location')['lat'], data.get('location')['lon']
    data_weather['lat'], data_weather['lon'] = lat, lon
    if data:
        return data_weather
    return None


def get_timezone_id(location_name):
    """
    Fetch the timezone ID (tz_id) for a given location using the WeatherAPI.
    Used to collect past data
    """
    try:
        params = {'q': location_name}
        data = get_weather_data('current', params)
        
        if data and 'location' in data:
            tz_id = data['location'].get('tz_id')
            return tz_id
        else:
            print("Error: 'location' data not found in the response.")
            return None
    except Exception as e:
        print(f"Error fetching timezone ID: {str(e)}")
        return None