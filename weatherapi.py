import time
from datetime import date
from datetime import timedelta

import pyowm


# Open Weather Map API
# My API Key: 95e49145dd2f7199e468eceb3e9acca9


# Weather Class
class WeatherAPI:
    def __init__(self, location):
        self.location = location
        self.owm = pyowm.OWM(API_key='95e49145dd2f7199e468eceb3e9acca9')
        self.time_since_last_forecast = time.time()
        self.update_time = 3600

    def best_description(self, list):
        description_rank = {'Snow': 1, 'Rain': 2, 'Clouds': 3, 'Clear': 4}
        if len(list) is 0:
            return None
        best = list[0]
        for status in list:
            if status not in description_rank:
                return None
            if description_rank[status] < description_rank[best]:
                best = status
        return best

    def get5DayForecast(self):
        #other_forecast = self.owm.daily_forecast('Golden, US')
        current_forecast = self.owm.three_hours_forecast_at_coords(self.location['lat'], self.location['lon'])
        print(current_forecast.when_snow())
        current_forecast = current_forecast.get_forecast()
        daily_forecast = []
        for i in range(5):
            day_weather = {}
            statuses = []
            for weather in current_forecast:
                if weather.get_reference_time('date').day is (date.today() + timedelta(days=i)).day:
                    # get status
                    statuses.append(weather.get_status())
                    # TODO: get rain/snow
                    # get temps
                    temps = weather.get_temperature('fahrenheit')
                    if 'min_temp' not in day_weather:
                        day_weather['min_temp'] = temps['temp_min']
                    elif temps['temp_min'] < day_weather['min_temp']:
                        day_weather['min_temp'] = temps['temp_min']

                    if 'max_temp' not in day_weather:
                        day_weather['max_temp'] = temps['temp_max']
                    elif temps['temp_max'] > day_weather['max_temp']:
                        day_weather['max_temp'] = temps['temp_max']

                    if 'temp' not in day_weather:
                        day_weather['temp'] = temps['temp_min']
                    else:
                        day_weather['temp'] += temps['temp_min']
                        day_weather['temp'] = day_weather['temp'] / 2
                    # get wind
                    if 'wind' not in day_weather:
                        day_weather['wind'] = weather.get_wind()['speed']
                    else:
                        day_weather['wind'] += weather.get_wind()['speed']
                        day_weather['wind'] = day_weather['wind'] / 2
            print((date.today() + timedelta(days=i)).day, statuses)
            day_weather['status'] = self.best_description(statuses)
            daily_forecast.append(day_weather)
        return daily_forecast


# Testing/example
if __name__ == "__main__":
    # Tuple to hold the current location
    current_location = {'lat': 39.7555, 'lon': -105.2211}
    # Create OWM instance using my api key
    golden_weather = WeatherAPI(current_location)
    forecast = golden_weather.get5DayForecast()
    print(forecast)
