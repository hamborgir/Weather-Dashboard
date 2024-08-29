import pycountry
from geopy.geocoders import GeoNames
from geopy.exc import GeocoderTimedOut
import pickle
import requests, os, sys
from datetime import datetime, timedelta
import pytz

class Weather:

    __country_names = list()
    __coord_dict = dict()

    def __init__(self):
        self.__init_coord()
        self.__country_names = list(self.__coord_dict.keys())

    def __fetch_country_coordinates(self, country_name, gn : GeoNames):
        try:
            location = gn.geocode(country_name)
            if location:
                return location.latitude, location.longitude
            else:
                return None, None
        except GeocoderTimedOut:
            return None, None

    def __init_coord(self):
        username = "hamb"
        coord_file = "coordinates.pkl"

        if os.path.exists(coord_file):
            with open(coord_file, 'rb') as file:
                self.__coord_dict = pickle.load(file)
            return

        gn = GeoNames(username)

        countries_coordinates = []

        for country in pycountry.countries:
            latitude, longitude = self.__fetch_country_coordinates(country.name, gn)
            if latitude is not None and longitude is not None:
                utc_offset = self.__fetch_utc_offset(latitude, longitude)
                countries_coordinates.append({
                    "country": country.name,
                    "latitude": latitude,
                    "longitude": longitude,
                    "utc_offset": utc_offset
                })

        coord_dict = {x['country']: (x['latitude'], x['longitude'], x['utc_offset']) for x in countries_coordinates}

        with open(coord_file, 'wb') as file:
            pickle.dump(coord_dict, file)
        
        self.__coord_dict = coord_dict

    def __fetch_utc_offset(self, latitude, longitude):
        try:
            tz = pytz.timezone(pytz.country_timezones('US')[0])  # Default to US, replace with appropriate logic
            utc_offset_seconds = tz.utcoffset(datetime.now()).total_seconds()
            return utc_offset_seconds / 3600  # convert to hours
        except Exception as e:
            print(f"Error fetching UTC offset: {e}")
            return None

    def fetch_weather_data(self, country: str):
        api_fmt = "https://api.open-meteo.com/v1/forecast?latitude=%f&longitude=%f&hourly=temperature_2m,relative_humidity_2m,precipitation_probability,cloud_cover,visibility,wind_speed_10m,uv_index,is_day&timezone=GMT"
        latitude, longitude, utc_offset = self.get_longlat(country)

        if longitude is None and latitude is None:
            raise NameError(f"No country entry with that name, {country}.")

        api = api_fmt % (latitude, longitude)
        response = requests.get(api)

        if response.status_code == 200:
            return response.json(), utc_offset
        else:
            return None, None

    @staticmethod
    def parse_weather_data(response: dict):
        hourly_data = response['hourly']
        hourly_units = response['hourly_units']

        parsed_data = []
        for i in range(len(hourly_data['time'])):
            entry = {
                'time': hourly_data['time'][i],
                'temperature_2m': hourly_data['temperature_2m'][i],
                'relative_humidity_2m': hourly_data['relative_humidity_2m'][i],
                'precipitation_probability': hourly_data['precipitation_probability'][i],
                'cloud_cover': hourly_data['cloud_cover'][i],
                'visibility': hourly_data['visibility'][i],
                'wind_speed_10m': hourly_data['wind_speed_10m'][i],
                'uv_index': hourly_data['uv_index'][i],
                'is_day': hourly_data['is_day'][i]
            }
            parsed_data.append(entry)

        return parsed_data, hourly_units

    @staticmethod
    def get_local_time(utc_time_str: str, utc_offset: float) -> str:
        utc_time = datetime.fromisoformat(utc_time_str)
        local_time = utc_time + timedelta(hours=utc_offset)
        return local_time.isoformat()

    def get_longlat(self, country: str):
        return self.__coord_dict.get(country, (None, None, None))
    
    @property
    def get_coord_dict(self):
        return self.__coord_dict
    
    @property
    def get_country_names(self):
        return self.__country_names

if __name__ == "__main__":
    weather = Weather()

    weather_data, utc_offset = weather.fetch_weather_data("Indonesia")
    if weather_data:
        parsed_data, units = Weather.parse_weather_data(weather_data)
        for entry in parsed_data:
            local_time = Weather.get_local_time(entry['time'], utc_offset)
            print(f"Local time: {local_time}, Temperature: {entry['temperature_2m']} {units['temperature_2m']}")
