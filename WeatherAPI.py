import time

from TimeOfDay import TimeOfDay
from WeatherShape import WeatherShape
from forecastiopy import *
from forecastiopy.FIOCurrently import FIOCurrently
from forecastiopy.FIODaily import FIODaily
from forecastiopy.FIOHourly import FIOHourly

# Open Weather Map API
# My API Key: 95e49145dd2f7199e468eceb3e9acca9

# Dark Sky API
# Key: 58bd3b25da2aae9c321d6f35183c2a8d
# Free up to 1000 requests per day

# Desired Weather data:
#   For current: precipProbability, temperature, apparentTemperature
#   For hourly:
#       Hour
#   For forecast: daily.summary, icon, precipProbability, precipType, temperature, temperatureHigh, temperatureLow, apparentTemperatureMin, apparentTemperatureMax

RAIN_SNOW_THRESHOLD = 0.1
CLOUD_COVER_THRESHOLD = 0.1
WEATHER_UPDATE_TIME = 100


class BaseWeather:
    def __init__(self):
        self.precipProbability = 0
        self.precipType = None
        self.cloudCover = 0
        self.uv = 0
        self.timeDay = TimeOfDay.DAY
        self.shape = WeatherShape.SUN
        self.summary = ''

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
            weather['fill%'] = self.uv // 11
            weather['value'] = f'{self.uv}'
            weather['unit'] = 'UV'
        elif self.timeDay == TimeOfDay.NIGHT:
            weather['shape'] = WeatherShape.MOON
        else:
            print('Unknown shape')
            exit(0)
        # set others
        weather['summary'] = self.summary

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
    def __init__(self, location):
        self.location = location
        self.time_since_last_forecast = time.time()
        self.update_time = 3600
        self.fio = ForecastIO.ForecastIO('58bd3b25da2aae9c321d6f35183c2a8d',
                                         units=ForecastIO.ForecastIO.UNITS_US,
                                         lang=ForecastIO.ForecastIO.LANG_ENGLISH,
                                         latitude=self.location['lat'], longitude=self.location['lon'])

    def update(self):
        if self.time_since_last_forecast > self.update_time:
            self.fio = ForecastIO.ForecastIO('58bd3b25da2aae9c321d6f35183c2a8d', units=ForecastIO.ForecastIO.UNITS_US,
                                             lang=ForecastIO.ForecastIO.LANG_ENGLISH, latitude=self.location['lat'],
                                             longitude=self.location['lon'])

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
                hour_weather.summary = hourly.get(hour)['summary']
                hour_weather.precipProbability = hourly.get(hour)['precipProbability']
                hour_weather.temperature = hourly.get(hour)['temperature']
                hour_weather.apparentTemperature = hourly.get(hour)['apparentTemperature']
                hour_weather.cloudCover = hourly.get(hour)['cloudCover']
                hour_weather.uv = hourly.get(hour)['uvIndex']
                try:
                    hour_weather.precipType = hourly.get(hour)['precipType']
                except KeyError:
                    print('darksky returned no precipType for hour')

                if self.fio.has_daily() is True:
                    daily = FIODaily(self.fio)
                    if hourly.get(hour)['time'] < daily.day_1_sunriseTime and hourly.get(hour)[
                        'time'] < daily.day_1_sunsetTime:
                        hour_weather.timeDay = TimeOfDay.NIGHT
                    else:
                        hour_weather.timeDay = TimeOfDay.DAY
                hourly_weather.append(hour_weather)
        else:
            print('No Hourly data')

        if self.fio.has_daily() is True:
            daily = FIODaily(self.fio)
            print('Summary:', daily.summary)

            # get current precipType
            if current_weather.precipType is None:
                try:
                    current_weather.precipType = daily.day_1_precipType
                except AttributeError:
                    print('darksky returned no precipType for daily')

            # get Time of Day for current
            if time.time() < daily.day_1_sunriseTime and time.time() < daily.day_1_sunsetTime:
                current_weather.timeDay = TimeOfDay.NIGHT
            else:
                current_weather.timeDay = TimeOfDay.DAY

            # get forecast weather
            for day in range(2, daily.days()):
                day_weather = BaseWeather()
                day_weather.summary = daily.get(day)['summary']
                day_weather.precipProbability = daily.get(day)['precipProbability']
                day_weather.highTemperature = daily.get(day)['temperatureHigh']
                day_weather.lowTemperature = daily.get(day)['temperatureLow']
                day_weather.cloudCover = daily.get(day)['cloudCover']
                day_weather.uv = daily.get(day)['uvIndex']
                try:
                    day_weather.precipType = daily.get(day)['precipType']
                except KeyError:
                    print('darksky returned no precipType for daily')
                day_weather.timeDay = TimeOfDay.DAY
                forecast_weather.append(day_weather)
        else:
            print('No Daily data')

        print(current_weather.get())
        for hour in hourly_weather:
            print(hour.get())
        for day in forecast_weather:
            print(day.get())


# Testing/example
if __name__ == "__main__":
    # Tuple to hold the current location
    current_location = {'lat': 39.7555, 'lon': -105.2211}
    # Create OWM instance using my api key
    golden_weather = WeatherAPI(current_location)

    while True:
        golden_weather.update()
        time.sleep(10)
