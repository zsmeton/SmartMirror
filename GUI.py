import pygame
from PIL import Image, ImageDraw
from pygame import Color, draw
from pygame.sprite import DirtySprite, LayeredDirty
from WeatherShape import WeatherShape
from Display import WIDTH, HEIGHT

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
        self.image = pygame.Surface([self.diameter, self.diameter])
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
        print(self.shape, self.shape_file_name, self.shape.shape_to_image())
        self.ending_angle = FILL_TO_ANGLE - fill * FILL_TO_ANGLE
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
        self.image = pygame.Surface([self.width, self.height])
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
            sprite.rect.topleft = (i * grid_width + i*(1 + 1/(len(self.sprites)-1))*self.padding, 0)

    def update(self):
        """
        Update redraws all of the sprites the SpriteGridContains
        """

        # update layout
        self.do_layout()

        # update sprites
        for sprite in self.sprites:
            sprite.update()

        # draw sprites
        for icon in self.sprites:
            self.image.blit(icon.image, icon.rect)
            print(icon.rect)
        self.dirty = 0


class WeatherWidget(DirtySprite):
    # Create Widgets Dirty Sprites
    current_weather_icon = WeatherIcon(diameter=(WIDTH if WIDTH < HEIGHT else HEIGHT) // 10)
    hour_grid = SpriteGrid(width=WIDTH / 4)
    days_grid = SpriteGrid(width = WIDTH/4)

    def __init__(self, *groups):
        super().__init__(*groups)
        # set icon locations
        self.current_weather_icon.move(int(0.75 * WIDTH), int(0.10 * HEIGHT))
        self.hour_grid.move(int(0.75 * WIDTH), int(0.2 * HEIGHT))
        self.days_grid.move(int(0.75 * WIDTH), int(0.4 * HEIGHT))
        self.image = pygame.Surface([WIDTH, HEIGHT])
        self.rect = self.image.get_rect()

    def set_weather(self, weather_dict):
        self.current_weather_icon.set_icon(shape=weather_dict['current']['shape'],
                                           fill=weather_dict['current']['fill%'])
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

    def update(self):
        self.current_weather_icon.update()
        self.hour_grid.update()
        self.days_grid.update()
        self.image.blit(self.current_weather_icon.image, self.current_weather_icon.rect)
        self.image.blit(self.hour_grid.image, self.hour_grid.rect)
        self.image.blit(self.days_grid.image, self.days_grid.rect)
