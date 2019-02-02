from json import JSONEncoder

from TimeOfDay import TimeOfDay
from WeatherShape import WeatherShape


# Custom encoder for weather objects
class WeatherEncoder(JSONEncoder):
    def default(self, obj):
        if type(obj) == WeatherShape:
            return {"__weather_enum__": str(obj)}
        elif type(obj) == TimeOfDay:
            return {"__time_enum__": str(obj)}
        else:
            JSONEncoder.default(self, obj)

# custom decoder hook for weather objects
def as_enum(d):
    if "__weather_enum__" in d:
        name, member = d["__weather_enum__"].split(".")
        return getattr(WeatherShape[name], member)
    elif "__time_enum__" in d:
        name, member = d["__time_enum__"].split(".")
        return getattr(TimeOfDay[name], member)
    else:
        return d

