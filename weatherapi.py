import json
import time
from datetime import datetime

from TimeOfDay import TimeOfDay
from WeatherJSON import WeatherEncoder
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

RAIN_SNOW_THRESHOLD = 0.10
CLOUD_COVER_THRESHOLD = 0.2
WEATHER_UPDATE_TIME = 110


# TODO: Moons are showing up as suns...

class BaseWeather:
    def __init__(self):
        self.precipProbability = 0
        self.precipType = None
        self.cloudCover = 0
        self.uv = 0
        self.moonPhase = 0
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
            weather['fill%'] = self.moonPhase
            weather['value'] = "%"
            weather['unit'] = f"{self.moonPhase*100}"
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
    current = None
    replacement_dict = {'(': '', ')': '', '°F': ' degrees fahrenheit', 'in.': 'inches', '-': 'to', '<': 'less than',
                        '>': 'greater than'}

    def __init__(self, location, writeFile):
        self.location = location
        self.time_since_last_forecast = 0
        self.update_time = WEATHER_UPDATE_TIME
        self.writeFile = writeFile
        self.fio = ForecastIO.ForecastIO('58bd3b25da2aae9c321d6f35183c2a8d',
                                         units=ForecastIO.ForecastIO.UNITS_US,
                                         lang=ForecastIO.ForecastIO.LANG_ENGLISH,
                                         latitude=self.location['lat'], longitude=self.location['lon'])
        self.current_weather = None
        self.hourly_weather = None
        self.forecast_weather = None
        self.week_summary = None

    def update(self):
        # If in update period
        if abs(self.time_since_last_forecast - time.time()) > self.update_time:
            # get new forecast
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

    @staticmethod
    def get_instance():
        return WeatherAPI.current

    def update_hourly_weather(self):
        """
        Sets the weather information for the upcoming hours

        :return: list of weather data for each hour
        """
        self.hourly_weather = []
        daily = None
        if self.fio.has_daily() is True:
            daily = FIODaily(self.fio)

        if self.fio.has_hourly() is True:
            hourly = FIOHourly(self.fio)
            for hour in range(2, 13, 2):
                hour_weather = SmallWeather()
                hour_data = hourly.get(hour)
                hour_weather.precipProbability = hour_data['precipProbability']
                hour_weather.temperature = hour_data['temperature']
                hour_weather.apparentTemperature = hour_data['apparentTemperature']
                hour_weather.cloudCover = hour_data['cloudCover']
                hour_weather.uv = hour_data['uvIndex']
                hour_weather.time = datetime.fromtimestamp(hour_data['time']).strftime('%I %p')
                hour_weather.summary = f"At {hour_weather.time[:-3]} o'clock, it will be {self._grammar_injection('ing', hour_data['summary'], 'y')} and the temperature will be {round(hour_data['apparentTemperature'])} degrees fahrenheit."
                try:
                    hour_weather.precipType = hour_data['precipType']
                except KeyError:
                    print('darksky returned no precipType for hour', datetime.fromtimestamp(hour_data['time']))

                # use sunset information to set the hours time of day
                if daily is not None:
                    if hour_data['time'] > daily.day_2_sunsetTime:
                        hour_weather.timeDay = TimeOfDay.NIGHT
                    else:
                        hour_weather.timeDay = TimeOfDay.DAY

                self.hourly_weather.append(hour_weather)
            return self.hourly_weather
        print('No Hourly data')
        return None

    def update_daily_weather(self):
        """
        Sets the weather information for the upcoming days

        :return: list of weather data for each day
        """
        self.forecast_weather = []
        if self.fio.has_daily() is True:
            daily = FIODaily(self.fio)
            self.week_summary = self._correct_punctuation(daily.daily['summary'], self.replacement_dict)
            # get forecast weather
            for day in range(2, daily.days()):
                day_weather = ForecastWeather()
                day_data = daily.get(day)
                day_weather.summary = self._correct_punctuation(day_data['summary'], self.replacement_dict)
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
                self.forecast_weather.append(day_weather)
            return self.forecast_weather
        else:
            print('No Daily data')
            return None

    def update_current_weather(self):
        """
        Sets the weather information for the current conditions

        :return: current weather
        """
        self.current_weather = SmallWeather()
        if self.fio.has_currently() is True:
            currently = FIOCurrently(self.fio)
            # fill in self.current_weather
            self.current_weather.precipProbability = currently.precipProbability
            self.current_weather.temperature = currently.temperature
            self.current_weather.apparentTemperature = currently.apparentTemperature
            self.current_weather.cloudCover = currently.cloudCover
            self.current_weather.uv = currently.uvIndex
            self.current_weather.summary = f"Currently it is {self._grammar_injection('ing', currently.summary, 'y')}, the temperature is {round(currently.apparentTemperature)} degrees fahrenheit."
            try:
                self.current_weather.precipType = currently.precipType
            except AttributeError:
                print('darksky returned no precipType for currently')

            if self.fio.has_daily() is True:
                daily = FIODaily(self.fio)
                # Check for a y in the first word for grammar
                self.current_weather.summary = self.current_weather.summary + self._correct_grammar(
                    "Today there will be", "Today it will be", daily.day_2_summary, "y")
                # Add high and low tot summary
                self.current_weather.summary = self.current_weather.summary[
                                               :-1] + f", with highs in the {int(round(daily.day_2_apparentTemperatureHigh,-1))}s and lows in the {int(round(daily.day_2_apparentTemperatureLow,-1))}s."
                # get current precipType
                if self.current_weather.precipType is None:
                    try:
                        self.current_weather.precipType = daily.day_2_precipType
                    except AttributeError:
                        print('darksky returned no precipType for daily',
                              datetime.fromtimestamp(daily.day_2_time))
                # get Time of Day for current
                if time.time() > daily.day_2_sunsetTime:
                    self.current_weather.timeDay = TimeOfDay.NIGHT
                    self.current_weather.moonPhase = daily.day_2_moonPhase
                else:
                    self.current_weather.timeDay = TimeOfDay.DAY

            return self.current_weather

        else:
            print('No Currently data')
            return None

    def get_weather(self):
        # Store weather details
        self.current_weather = self.update_current_weather()
        self.hourly_weather = self.update_hourly_weather()
        self.forecast_weather = self.update_daily_weather()

        print(self.current_weather.summary, self.week_summary, self.forecast_weather[0].summary,
              self.hourly_weather[0].summary, sep='\n')

        hourly_data = []
        for hour in self.hourly_weather:
            hourly_data.append(hour.get())
        forecast_data = []
        for day in self.forecast_weather:
            forecast_data.append(day.get())
        return {'current': self.current_weather.get(), 'hourly': hourly_data, 'forecast': forecast_data}

    def _correct_grammar(self, string_a, string_b, input, switch):
        """
        if the first word of input does not contains switch this will return string_a + input
        else it will return string_b + input

        :param string_a: a string to concatonate to input
        :param string_b: a string to concatonate to input
        :param input: the string being concatonated
        :param switch_string: the set of strings to look for in the first word of input
        """
        if switch.lower() in str(input).split(" ", 1)[0].lower():
            return f" {string_b} {input}"
        return f" {string_a} {input}"

    def _grammar_injection(self, string_a, string, switch):
        """
        if the first word of input does not contains switch this will return input
        else it will return the first word of input input + string_a + rest of input

        :param string_a: a string to inject into input
        :param string: the string being concatonated
        :param switch_string: the set of strings to look for in the first word of input
        """
        if switch.lower() not in str(string).split(" ", 1)[0].lower():
            if len(str(string).split(" ", 1)) > 1:
                return f"{str(string).split(' ', 1)[0]}{string_a} {str(string).split(' ', 1)[1]}"
            else:
                return f" {str(string).split(' ', 1)[0]}{string_a}"
        return string

    def _correct_punctuation(self, string: str, replacement_dict: dict):
        for key, value in replacement_dict.items():
            string = string.replace(key, value)
        return string


# Testing/example
if __name__ == "__main__":
    # Tuple to hold the current location
    current_location = {'lat': 39.7555, 'lon': -105.2211}
    # Create OWM instance using my api key
    golden_weather = WeatherAPI(current_location, writeFile='weather.txt')

    while True:
        golden_weather.update()
        time.sleep(10)
