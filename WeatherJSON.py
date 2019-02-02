from json import JSONEncoder
from WeatherShape import WeatherShape
from TimeOfDay import TimeOfDay

class WeatherDecoder(JSONEncoder):
    def default(self, obj):
        if type(obj) in WeatherShape.values():
            return {"__weather_enum__": str(obj)}
        elif type(obj) in TimeOfDay.values():
            return {"__time_enum__": str(obj)}
        else: