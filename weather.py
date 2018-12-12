import pyowm
# Open Weather Map API
# My API Key: 95e49145dd2f7199e468eceb3e9acca9

# Weather Class
class Weather:
    def __init__(self, location):
        self.location = location
        self.owm = pyowm.OWM(API_key='95e49145dd2f7199e468eceb3e9acca9')


# Testing/example
if __name__ == "__main__":
    # Tuple to hold the current location
    current_location = {'lat': 37.09024, 'lon': -95.712891}
    # Create OWM instance using my api key
    owm = pyowm.OWM(API_key='95e49145dd2f7199e468eceb3e9acca9')
    # Create observation instance for Current Location
    observation = owm.weather_at_coords(lat=current_location['lat'], lon=current_location['lon'])
    # Get the weather data from that observation
    current_weather = observation.get_weather()
    print(current_weather.get_wind())
    print(current_weather.get_rain())
    print(current_weather.get_snow())
    print(current_weather.get_clouds())
    print(current_weather.get_temperature(unit='fahrenheit'))
    print(current_weather.get_clouds())
