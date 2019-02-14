import pygame
from PIL import Image, ImageDraw
from pygame import Color, draw
from pygame.sprite import DirtySprite, LayeredDirty

from Display import WIDTH, HEIGHT
from MathExtension import variable_mapping
from WeatherShape import WeatherShape

# Constants
FILL_TO_ANGLE = 360


def pil_to_pygame_image(pil_image: Image) -> pygame.image:
    """
    Converts PIL images to pygame images
    :param pil_image: the pil image to convert
    :return: a pygame.image object
    """
    mode = pil_image.mode
    size = pil_image.size
    data = pil_image.tobytes()
    image = pygame.image.fromstring(data, size, mode)
    return image


class WeatherIcon(DirtySprite):
    # Properties
    fill_color = (51, 255, 255)
    unfilled_color = Color(100, 100, 100)
    shape_file_name = ""
    starting_angle = 0
    ending_angle = 0
    diameter = 100
    shape = WeatherShape.SUN

    def __init__(self, *groups, **kwargs):
        super().__init__(*groups)
        self.__dict__.update(kwargs)
        self.image = pygame.Surface([self.diameter, self.diameter], pygame.SRCALPHA)
        self.image.fill(self.unfilled_color)
        self.rect = self.image.get_rect()

    def set_icon(self, shape: WeatherShape, fill: float):
        """
        Sets the WeatherIcon's shape (image) and fill percentile
        :param shape:
        :param fill:
        """
        self.shape = shape
        self.shape_file_name = self.shape.shape_to_image()
        self.starting_angle = fill * FILL_TO_ANGLE
        self.dirty = 1
        return self

    def move(self, x: int = 0, y: int = 0):
        """
        Moves the WeatherIcon center to the x amd y pos, x and y default to 0
        :param x:
        :param y:
        """
        self.rect.center = (x, y)

    def resize(self, width, height):
        self.diameter = width
        self.image = pygame.Surface([self.diameter, self.diameter])
        self.image.fill(self.unfilled_color)
        self.rect = self.image.get_rect()
        self.dirty = 1

    def update(self):
        """
        Update redraws the image for the WeatherIcon only if the object has just been initialized or set_icon() has
        been called recently.
        """
        if self.dirty:
            # create a rectangle the size of the sprites rectangle
            draw.rect(self.image, self.unfilled_color, self.rect)

            # create a pie image filled to the percentage
            pil_image = Image.new("RGBA", (self.diameter, self.diameter))
            pil_draw = ImageDraw.Draw(pil_image)
            pil_draw.pieslice((0, 0, self.diameter, self.diameter), self.ending_angle, self.starting_angle,
                              fill=self.fill_color)

            # convert pie image into PyGame image

            py_image = pil_to_pygame_image(pil_image)
            py_image_rect = py_image.get_rect(center=self.image.get_rect().center)
            self.image.blit(py_image, py_image_rect)

            # add icon to the rectangle
            pil_icon_image = Image.open(self.shape_file_name)
            pil_icon_image = pil_icon_image.resize(self.rect.size)
            icon_image = pil_to_pygame_image(pil_icon_image)
            icon_image_rect = icon_image.get_rect(center=self.image.get_rect().center)
            self.image.blit(icon_image, icon_image_rect)

            self.dirty = 0


class SpriteGrid(DirtySprite):
    # Properties
    sprites = []
    background_color = Color(0)
    width = 100
    height = 100
    padding = 10

    def __init__(self, *members, **kwargs):
        super().__init__()
        for sprite in members:
            self.sprites.append(sprite)

        self.__dict__.update(kwargs)
        self.image = pygame.Surface([self.width, self.height], pygame.SRCALPHA)
        self.image.fill(self.background_color)
        self.rect = self.image.get_rect()

    def move(self, x: int = 0, y: int = 0):
        """
        Moves the WeatherIcon center to the x amd y pos, x and y default to 0
        :param x:
        :param y:
        """
        self.rect.center = (x, y)
        self.dirty = 1

    def update_icons(self, *args):
        self.sprites = []
        for sprite in args:
            self.sprites.append(sprite)
        self.dirty = 1

    def do_layout(self):
        old_center_location = self.rect.center

        # figure out the width of each grid
        grid_width = (self.width / len(self.sprites)) - self.padding
        if grid_width < 10:
            print("Grid Width calulation results in a non positive image width which is impossible, make width larger")
            exit(-5)

        new_height = 0
        # set sprites height and width
        for sprite in self.sprites:
            ratio = sprite.rect.height / sprite.rect.width
            # set height to the correct ratio from old width to grid_width
            sprite.resize(int(grid_width), int(grid_width * ratio))

            if sprite.rect.height > new_height:
                new_height = sprite.rect.height

        # set the grid height to the biggest widget height
        self.height = new_height

        # update image and rect
        self.image = pygame.Surface([self.width, self.height])
        self.rect = self.image.get_rect()
        self.rect.center = old_center_location

        # set sprite center locations
        for i, sprite in enumerate(self.sprites):
            sprite.rect.topleft = (i * grid_width + i * (1 + 1 / (len(self.sprites) - 1)) * self.padding, 0)

    def update(self):
        """
        Update redraws all of the sprites the SpriteGridContains
        """
        if self.dirty or any(elem.dirty for elem in self.sprites):
            # update layout
            self.do_layout()

            # update sprites
            for sprite in self.sprites:
                sprite.update()

            # draw sprites
            for icon in self.sprites:
                self.image.blit(icon.image, icon.rect)
            self.dirty = 0


class TemperatureGraph(DirtySprite):
    # Properties
    num_of_graphs = 1
    temperatures = []
    background_color = Color(0, 0, 0, 0)
    line_colors = Color(255, 255, 255)
    dot_color = Color(0)
    width = 100
    height = 100
    antialiased = False
    thickness = 3

    def __init__(self, *members, **kwargs):
        super().__init__()
        self.__dict__.update(kwargs)
        self.image = pygame.Surface([self.width, self.height], pygame.SRCALPHA)
        self.image.fill(self.background_color)
        self.rect = self.image.get_rect()

    def set_temperatures(self, *args):
        """
        Sets the graphs temperature values to the passed in args
        :param args: temperature values
        """
        # clear temperatures
        self.temperatures = []
        # add new temperatures
        if self.num_of_graphs > 1:
            for i in range(0, self.num_of_graphs):
                line_temperatures = []
                for temps in args[i]:
                    line_temperatures.append(int(temps))
                self.temperatures.append(line_temperatures)
        else:
            for temps in args:
                self.temperatures.append(int(temps))
        self.dirty = 1

    def move(self, x: int = 0, y: int = 0):
        """
        Moves the WeatherIcon center to the x amd y pos, x and y default to 0
        :param x: x position
        :param y: y position
        """
        self.rect.center = (x, y)

    def update(self):
        """
        Updates the graphics if the object has just been created or set_temperatures has been called
        """
        max_temp = None
        min_temp = None
        temp_x_spacing = None
        if self.dirty:
            if self.num_of_graphs > 1:
                for i in range(0, self.num_of_graphs):
                    # find max and min temperatures for y spacing
                    if max_temp is None or max(self.temperatures[i]) > max_temp:
                        max_temp = max(self.temperatures[i])
                    if min_temp is None or min(self.temperatures[i]) < min_temp:
                        min_temp = min(self.temperatures[i])
            else:
                # find max and min temperatures for y spacing
                max_temp = max(self.temperatures)
                min_temp = min(self.temperatures)
                temp_x_spacing = (self.width / len(self.temperatures))

            # draw line(s)
            if self.num_of_graphs > 1:
                for i in range(0, self.num_of_graphs):
                    temp_x_spacing = (self.width / len(self.temperatures[i]))
                    # create a point list for the temperatures
                    point_list = []
                    for x, temp in enumerate(self.temperatures[i]):
                        point_list.append([x * temp_x_spacing + temp_x_spacing / 2,
                                           variable_mapping(temp, min_temp, max_temp, 0, self.height)])
                    if self.antialiased:
                        draw.aalines(self.image, self.line_colors[i], False, point_list)
                    else:
                        draw.lines(self.image, self.line_colors[i], False, point_list, self.thickness)

            else:
                point_list = []
                for i, temp in enumerate(self.temperatures):
                    point_list.append([i * temp_x_spacing + temp_x_spacing / 2,
                                       variable_mapping(temp, min_temp, max_temp, 0, self.height)])
                if self.antialiased:
                    draw.aalines(self.image, self.line_color, False, point_list)
                else:
                    draw.lines(self.image, self.line_colors[i], False, point_list, self.thickness)


class WeatherWidget(DirtySprite):
    # Create Widgets Dirty Sprites
    current_weather_icon = WeatherIcon(diameter=(WIDTH if WIDTH < HEIGHT else HEIGHT) // 10)
    hour_grid = SpriteGrid(width=WIDTH / 4)
    days_grid = SpriteGrid(width=WIDTH / 4)
    hour_temperatures = TemperatureGraph(width=WIDTH / 4, height=HEIGHT / 10,
                                         line_colors=[Color(255, 214, 51), Color(255, 52, 144)], num_of_graphs=2)
    day_temperatures = TemperatureGraph(width=WIDTH / 4, height=HEIGHT / 10,
                                        line_colors=[Color(255, 214, 51), Color(255, 52, 144)], num_of_graphs=2)

    sprites = LayeredDirty()
    sprites.add(current_weather_icon, hour_grid, days_grid, hour_temperatures, day_temperatures)

    def __init__(self, *groups):
        super().__init__(*groups)
        # set icon locations
        self.current_weather_icon.move(int(0.75 * WIDTH), int(0.10 * HEIGHT))
        self.hour_grid.move(int(0.75 * WIDTH), int(0.2 * HEIGHT))
        self.days_grid.move(int(0.75 * WIDTH), int(0.4 * HEIGHT))
        self.hour_temperatures.move(int(0.75 * WIDTH), int(0.3 * HEIGHT))
        self.day_temperatures.move(int(0.75 * WIDTH), int(0.5 * HEIGHT))

        # create object surface and rectangle
        self.image = pygame.Surface([WIDTH, HEIGHT])
        self.rect = self.image.get_rect()

    def set_weather(self, weather_dict):
        """
        Sets the weather of all corresponding graphics
        :param weather_dict: weather dict created by WeatherAPI
        """
        self.current_weather_icon.set_icon(shape=weather_dict['current']['shape'],
                                           fill=weather_dict['current']['fill%'])
        print(weather_dict['current']['fill%'] * FILL_TO_ANGLE)
        self.hour_grid.update_icons(WeatherIcon().set_icon(shape=weather_dict['hourly'][0]['shape'],
                                                           fill=weather_dict['hourly'][0]['fill%']),
                                    WeatherIcon().set_icon(shape=weather_dict['hourly'][1]['shape'],
                                                           fill=weather_dict['hourly'][1]['fill%']),
                                    WeatherIcon().set_icon(shape=weather_dict['hourly'][2]['shape'],
                                                           fill=weather_dict['hourly'][2]['fill%']),
                                    WeatherIcon().set_icon(shape=weather_dict['hourly'][3]['shape'],
                                                           fill=weather_dict['hourly'][3]['fill%']),
                                    WeatherIcon().set_icon(shape=weather_dict['hourly'][4]['shape'],
                                                           fill=weather_dict['hourly'][4]['fill%']))
        self.days_grid.update_icons(WeatherIcon().set_icon(shape=weather_dict['forecast'][0]['shape'],
                                                           fill=weather_dict['forecast'][0]['fill%']),
                                    WeatherIcon().set_icon(shape=weather_dict['forecast'][1]['shape'],
                                                           fill=weather_dict['forecast'][1]['fill%']),
                                    WeatherIcon().set_icon(shape=weather_dict['forecast'][2]['shape'],
                                                           fill=weather_dict['forecast'][2]['fill%']),
                                    WeatherIcon().set_icon(shape=weather_dict['forecast'][3]['shape'],
                                                           fill=weather_dict['forecast'][3]['fill%']),
                                    WeatherIcon().set_icon(shape=weather_dict['forecast'][4]['shape'],
                                                           fill=weather_dict['forecast'][4]['fill%']),
                                    WeatherIcon().set_icon(shape=weather_dict['forecast'][5]['shape'],
                                                           fill=weather_dict['forecast'][5]['fill%']))
        self.hour_temperatures.set_temperatures([weather_dict['hourly'][0]['temperature'],
                                                 weather_dict['hourly'][1]['temperature'],
                                                 weather_dict['hourly'][2]['temperature'],
                                                 weather_dict['hourly'][3]['temperature'],
                                                 weather_dict['hourly'][4]['temperature']],
                                                [weather_dict['hourly'][0]['feels'],
                                                 weather_dict['hourly'][1]['feels'],
                                                 weather_dict['hourly'][2]['feels'],
                                                 weather_dict['hourly'][3]['feels'],
                                                 weather_dict['hourly'][4]['feels']])
        self.day_temperatures.set_temperatures([weather_dict['forecast'][0]['highTemperature'],
                                                weather_dict['forecast'][1]['highTemperature'],
                                                weather_dict['forecast'][2]['highTemperature'],
                                                weather_dict['forecast'][3]['highTemperature'],
                                                weather_dict['forecast'][4]['highTemperature']],
                                               [weather_dict['forecast'][0]['lowTemperature'],
                                                weather_dict['forecast'][1]['lowTemperature'],
                                                weather_dict['forecast'][2]['lowTemperature'],
                                                weather_dict['forecast'][3]['lowTemperature'],
                                                weather_dict['forecast'][4]['lowTemperature']])

    def update(self):
        """
        Update redraws all of the sprites in the WeatherWidget
        """
        self.sprites.update()
        self.sprites.draw(self.image)
