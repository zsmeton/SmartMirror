from enum import Enum
from os import path


# Enum of possible weather shapes along with
class WeatherShape(Enum):
    RAINDROP = 1
    SNOWFLAKE = 2
    CLOUD = 3
    SUN = 4
    MOON = 5

    def shape_to_image(self):
        """
        :return str: a path to the image representing the shape
        """
        image = {self.RAINDROP: path.join("weather", "raindrop.png"),
                 self.SNOWFLAKE: path.join("weather", "snowflake.png"),
                 self.CLOUD: path.join("weather", "cloud.png"),
                 self.SUN: path.join("weather", "sun.png"),
                 self.MOON: path.join("weather", "moon.png")}
        return image.get(self)


if __name__ == '__main__':
    for shape in WeatherShape:
        print(shape.shape_to_image())
