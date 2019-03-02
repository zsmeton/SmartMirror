import json
import time
from datetime import datetime

from TimeOfDay import TimeOfDay
from WeatherShape import WeatherShape
from WeatherJSON import WeatherEncoder
from forecastiopy import *
from forecastiopy.FIOCurrently import FIOCurrently
from forecastiopy.FIODaily import FIODaily
from forecastiopy.FIOHourly import FIOHourly

# Open Weather Map API
# My API Key: 95e49145dd2f7199e468eceb3e9acca9

# Dark Sky API
# Key: 58bd3b25da2aae9c321d6f35183c2a8d
# Free up to 1000 requests per day

RAIN_SNOW_THRESHOLD = 0.10
CLOUD_COVER_THRESHOLD = 0.2
WEATHER_UPDATE_TIME = 110


class BaseWeather:
    def __init__(self):
        self.precipProbability = 0
        self.precipType = None
        self.cloudCover = 0
        self.uv = 0
        self.timeDay = TimeOfDay.DAY
        self.shape = WeatherShape.SUN
        self.summary = ''
        self.time = 0

    def get(self) -> dict:
        self.uv = self.uv if self.uv < 11 else 11
        weather = {}
        # set display shape, fill%, value, and units
        if self.precipProbability >= RAIN_SNOW_THRESHOLD:
            if self.precipType == 'rain':
                weather['shape'] = WeatherShape.RAINDROP
            else:
                weather['shape'] = WeatherShape.SNOWFLAKE
            weather['fill%'] = self.precipProbability
            weather['value'] = f'{self.precipProbability*100}'
            weather['unit'] = '%'
        elif self.cloudCover >= CLOUD_COVER_THRESHOLD:
            weather['shape'] = WeatherShape.CLOUD
            weather['fill%'] = self.cloudCover
            weather['value'] = f'{self.cloudCover * 100}'
            weather['unit'] = '%'
        elif self.timeDay == TimeOfDay.DAY:
            weather['shape'] = WeatherShape.SUN
            weather['fill%'] = self.uv / 11
            weather['value'] = f'{self.uv}'
            weather['unit'] = 'UV'
        elif self.timeDay == TimeOfDay.NIGHT:
            weather['shape'] = WeatherShape.MOON
            weather['fill%'] = 1
            weather['value'] = ""
            weather['unit'] = ""
        else:
            print('Unknown shape')
            exit(0)
        # set others
        weather['summary'] = self.summary
        weather['time'] = self.time

        return weather


class SmallWeather(BaseWeather):
    def __init__(self):
        super().__init__()
        self.temperature = 0
        self.apparentTemperature = 0

    def get(self) -> dict:
        weather = super().get()
        weather['temperature'] = self.temperature
        weather['feels'] = self.apparentTemperature
        return weather


class ForecastWeather(BaseWeather):
    def __init__(self):
        super().__init__()
        self.highTemperature = 0
        self.lowTemperature = 0

    def get(self) -> dict:
        weather = super().get()
        weather['highTemperature'] = self.highTemperature
        weather['lowTemperature'] = self.lowTemperature
        return weather


# Weather Class
class WeatherAPI:

    def __init__(self, location, writeFile):
        self.location = location
        self.time_since_last_forecast = 0
        self.update_time = WEATHER_UPDATE_TIME
        self.writeFile = writeFile
        self.fio = ForecastIO.ForecastIO('58bd3b25da2aae9c321d6f35183c2a8d',
                                         units=ForecastIO.ForecastIO.UNITS_US,
                                         lang=ForecastIO.ForecastIO.LANG_ENGLISH,
                                         latitude=self.location['lat'], longitude=self.location['lon'])

    def update(self):
        if abs(self.time_since_last_forecast - time.time()) > self.update_time:
            self.fio = ForecastIO.ForecastIO('58bd3b25da2aae9c321d6f35183c2a8d', units=ForecastIO.ForecastIO.UNITS_US,
                                             lang=ForecastIO.ForecastIO.LANG_ENGLISH, latitude=self.location['lat'],
                                             longitude=self.location['lon'])
            print("Updating Weather information")
            # Write updated data to a file using json
            with open(self.writeFile, 'w') as fout:
                out = self.get_weather()
                json.dump(out, fout, cls=WeatherEncoder)
            # Update time since forecast
            self.time_since_last_forecast = time.time()

    def get_weather(self):
        # Store weather details
        current_weather = SmallWeather()
        hourly_weather = []
        forecast_weather = []

        # self.precipType = 'rain'

        if self.fio.has_currently() is True:
            currently = FIOCurrently(self.fio)
            # fill in current_weather
            current_weather.summary = currently.summary
            current_weather.precipProbability = currently.precipProbability
            current_weather.temperature = currently.temperature
            current_weather.apparentTemperature = currently.apparentTemperature
            current_weather.cloudCover = currently.cloudCover
            current_weather.uv = currently.uvIndex
            try:
                current_weather.precipType = currently.precipType
            except AttributeError:
                print('darksky returned no precipType for currently')

        else:
            print('No Currently data')

        if self.fio.has_hourly() is True:
            hourly = FIOHourly(self.fio)
            for hour in range(2, 13, 2):
                hour_weather = SmallWeather()
                hour_data = hourly.get(hour)
                hour_weather.summary = hour_data['summary']
                hour_weather.precipProbability = hour_data['precipProbability']
                hour_weather.temperature = hour_data['temperature']
                hour_weather.apparentTemperature = hour_data['apparentTemperature']
                hour_weather.cloudCover = hour_data['cloudCover']
                hour_weather.uv = hour_data['uvIndex']
                hour_weather.time = datetime.fromtimestamp(hour_data['time']).strftime('%I %p')
                try:
                    hour_weather.precipType = hour_data['precipType']
                except KeyError:
                    print('darksky returned no precipType for hour', datetime.fromtimestamp(hour_data['time']))

                if self.fio.has_daily() is True:
                    daily = FIODaily(self.fio)
                    if hour_data['time'] > daily.day_2_sunsetTime:
                        hour_weather.timeDay = TimeOfDay.NIGHT
                    else:
                        hour_weather.timeDay = TimeOfDay.DAY
                hourly_weather.append(hour_weather)
        else:
            print('No Hourly data')

        if self.fio.has_daily() is True:
            daily = FIODaily(self.fio)

            # get current precipType
            if current_weather.precipType is None:
                try:
                    current_weather.precipType = daily.day_1_precipType
                except AttributeError:
                    print('darksky returned no precipType for daily',
                          datetime.fromtimestamp(daily.day_1_time))

            # get Time of Day for current
            if time.time() > daily.day_2_sunsetTime:
                current_weather.timeDay = TimeOfDay.NIGHT
            else:
                current_weather.timeDay = TimeOfDay.DAY

            # get forecast weather
            for day in range(2, daily.days()):
                day_weather = ForecastWeather()
                day_data = daily.get(day)
                day_weather.summary = day_data['summary']
                day_weather.precipProbability = day_data['precipProbability']
                day_weather.highTemperature = day_data['temperatureHigh']
                day_weather.lowTemperature = day_data['temperatureLow']
                day_weather.cloudCover = day_data['cloudCover']
                day_weather.uv = day_data['uvIndex']
                day_weather.lowTemperature = day_data['temperatureMin']
                day_weather.highTemperature = day_data['temperatureMax']
                day_weather.time = datetime.fromtimestamp(day_data['time']).strftime('%A')
                try:
                    day_weather.precipType = day_data['precipType']
                except KeyError:
                    print('darksky returned no precipType for daily on date:', datetime.fromtimestamp(day_data['time']))
                day_weather.timeDay = TimeOfDay.DAY
                forecast_weather.append(day_weather)
        else:
            print('No Daily data')

        hourly_data = []
        for hour in hourly_weather:
            hourly_data.append(hour.get())
        forecast_data = []
        for day in forecast_weather:
            forecast_data.append(day.get())
        return {'current': current_weather.get(), 'hourly': hourly_data, 'forecast': forecast_data}


# Testing/example
if __name__ == "__main__":
    # Tuple to hold the current location
    current_location = {'lat': 39.7555, 'lon': -105.2211}
    # Create OWM instance using my api key
    golden_weather = WeatherAPI(current_location, writeFile='weather.txt')

    while True:
        golden_weather.update()
        time.sleep(10)
