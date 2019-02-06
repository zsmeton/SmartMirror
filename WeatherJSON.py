from json import JSONEncoder

from TimeOfDay import TimeOfDay
from WeatherShape import WeatherShape


# Custom encoder for weather objects
class WeatherEncoder(JSONEncoder):
    def default(self, obj):
        if type(obj) == WeatherShape:
            return {"__weather_enum__": str(obj.value)}
        elif type(obj) == TimeOfDay:
            return {"__time_enum__": str(obj.value)}
        else:
            JSONEncoder.default(self, obj)


def weather_hook(d):
    """
    Custom decoder hook for weather objects

    :param d: json dumped dictionary
    :return: python dictionary

    Example:
        text = json.dumps(data, cls=WeatherEncoder)
        json.loads(text, object_hook=weather_hook)
    """
    if "__weather_enum__" in d:
        value = int(d["__weather_enum__"])
        return WeatherShape(value)
    elif "__time_enum__" in d:
        value = int(d["__time_enum__"])
        return TimeOfDay(value)
    else:
        return d
