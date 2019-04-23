import math
import time
from datetime import datetime

import pygame
from PIL import Image, ImageDraw, ImageFont
from pygame import Color, draw, gfxdraw
from pygame.sprite import DirtySprite, LayeredDirty

from Display import WIDTH, HEIGHT
from MathExtension import variable_mapping
from WeatherShape import WeatherShape

pygame.font.init()

# Constants
FILL_TO_ANGLE = 360
TEXT_SIZES = {6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 20, 24, 26, 27, 28, 29, 30, 32, 34, 36}
FONT = 'Pillow/Tests/fonts/arial.ttf'


def get_text_size(proposed_size):
    if proposed_size in TEXT_SIZES:
        return proposed_size
    else:
        closest = None
        for i in range(-30, 30):
            if proposed_size + i in TEXT_SIZES:
                if closest is None:
                    closest = proposed_size + i
                elif abs(i) < abs(proposed_size - closest):
                    closest = proposed_size + i
        return closest


def grouped(iterable, n):
    """
    s -> (s0,s1,s2,...sn-1), (sn,sn+1,sn+2,...s2n-1), (s2n,s2n+1,s2n+2,...s3n-1), ... \n
    Turns a list into a list of tuples to then be iterated over\n
    source: "https://stackoverflow.com/questions/5389507/iterating-over-every-two-elements-in-a-list"

    :param iterable: The iterable object to be paired up
    :param n: how many objects per grouping
    :return: an iterable of grouped members

    Examples:\n
    l = [1,2,3,4,5,6]\n
    for i,k in grouped(l,2):
        print str(i), '+', str(k), '=', str(i+k)\n

    Output:\n
    1+2=3\n
    3+4=7\n
    5+6=11\n
    """
    return zip(*[iter(iterable)] * n)


def overlap_grouped(iterable):
    """
    Turns a list into a list of tuples to then be iterated over\n

    :param iterable: The iterable object to be paired up
    :return: an iterable of grouped members

    Examples:\n
    l = [1,2,3,4,5,6]\n
    for i,k in grouped(l,2,1):
        print str(i), '+', str(k), '=', str(i+k)\n

    Output:\n
    1+2=3\n
    2+3=5\n
    3+4=7\n
    4+5=9\n
    5+6=11\n
    """
    grouping = 2
    overlap = 1

    output = list()
    for i, first in enumerate(iterable):
        group = [first]
        if i == len(iterable) - 1:
            return output
        for j in range(i + grouping - overlap, i + grouping):
            group.append(iterable[j])
        output.append(tuple(group))
    return output


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


def get_aalines_surface(surface: pygame.Surface, points: list, thickness, color) -> pygame.Rect:
    """
    Draws the lines onto the surface given with thick antialiased lines using polygons
    based on: https://stackoverflow.com/questions/30578068/pygame-draw-anti-aliased-thick-line

    :param surface: Tyhe surface to draw the lines onto
    :param thickness: The desired thickness of the lines in pixels
    :param color: The desired color of the lines
    :param points: list of poinzts [x,y]
    :returns: a rectangle
    """
    for begin, end in overlap_grouped(points):
        center_L1 = [(begin[0] + end[0]) / 2, (begin[1] + end[1]) / 2]
        length = math.sqrt(abs(begin[0] - end[0]) ** 2 + abs(begin[1] - end[1]) ** 2)  # Line size
        angle = math.atan2(begin[1] - end[1], begin[0] - end[0])
        UL = (center_L1[0] + (length / 2.) * math.cos(angle) - (thickness / 2.) * math.sin(angle),
              center_L1[1] + (thickness / 2.) * math.cos(angle) + (length / 2.) * math.sin(angle))
        UR = (center_L1[0] - (length / 2.) * math.cos(angle) - (thickness / 2.) * math.sin(angle),
              center_L1[1] + (thickness / 2.) * math.cos(angle) - (length / 2.) * math.sin(angle))
        BL = (center_L1[0] + (length / 2.) * math.cos(angle) + (thickness / 2.) * math.sin(angle),
              center_L1[1] - (thickness / 2.) * math.cos(angle) + (length / 2.) * math.sin(angle))
        BR = (center_L1[0] - (length / 2.) * math.cos(angle) + (thickness / 2.) * math.sin(angle),
              center_L1[1] - (thickness / 2.) * math.cos(angle) - (length / 2.) * math.sin(angle))
        pygame.gfxdraw.aapolygon(surface, (UL, UR, BR, BL), color)
        pygame.gfxdraw.filled_polygon(surface, (UL, UR, BR, BL), color)


def arc(draw, bbox, start, end, fill, width=1, segments=100):
    """
    Hack that looks similar to PIL's draw.arc(), but can specify a line width.
    Source: https://stackoverflow.com/questions/7070912/creating-an-arc-with-a-given-thickness-using-pils-imagedraw
    """
    # radians
    start *= math.pi / 180
    end *= math.pi / 180

    # angle step
    da = (end - start) / segments

    # shift end points with half a segment angle
    start -= da / 2
    end -= da / 2

    # ellips radii
    rx = (bbox[2] - bbox[0]) / 2
    ry = (bbox[3] - bbox[1]) / 2

    # box centre
    cx = bbox[0] + rx
    cy = bbox[1] + ry

    # segment length
    l = (rx + ry) * da / 2.0

    for i in range(segments):
        # angle centre
        a = start + (i + 0.5) * da

        # x,y centre
        x = cx + math.cos(a) * rx
        y = cy + math.sin(a) * ry

        # derivatives
        dx = -math.sin(a) * rx / (rx + ry)
        dy = math.cos(a) * ry / (rx + ry)

        draw.line([(x - dx * l, y - dy * l), (x + dx * l, y + dy * l)], fill=fill, width=width)


def draw_arc(width, height, fill, thickness, color) -> pygame.image:
    """
    Draws an arc using PIL of the following properties, at a larger resolution, scales down for smoothing, and then returns as pygame image
    :param width:
    :param height:
    :param fill: float between 0-1
    :param thickness:
    :param color:
    :return pygame image:
    """
    AA_SCALING = 10
    image = Image.new('RGBA', (width * AA_SCALING, height * AA_SCALING), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    arc(draw=draw, bbox=[thickness * AA_SCALING, thickness * AA_SCALING, (width - thickness) * AA_SCALING,
                         (height - thickness) * AA_SCALING], start=0,
        end=variable_mapping(fill, 0, 1, 0, 360), fill=color, width=thickness * AA_SCALING, segments=1000)
    image = image.resize((width, height), resample=Image.ANTIALIAS)
    return pil_to_pygame_image(image)


class WeatherIcon(DirtySprite):
    FONT = 'Pillow/Tests/fonts/arial.ttf'

    def __init__(self, *groups, **kwargs):
        super().__init__(groups)
        self.fill_color = (102, 255, 255)
        self.unfilled_color = Color(100, 100, 100)
        self.shape_file_name = ""
        self.starting_angle = 0
        self.ending_angle = 0
        self.size = 100
        self.padding = round(WIDTH / 150) if round(WIDTH / 150) % 2 == 0 else round(WIDTH / 150) + 1
        self.shape = WeatherShape.SUN
        self.text_color = Color(255, 255, 255, 255)
        self.text_ratio = 4
        self.center_value = ""
        self.center_unit = ""
        self.top_right_value = ""
        self.top_right_unit = ""
        self.top_left_value = ""
        self.top_left_unit = ""
        self.bottom_right_value = ""
        self.bottom_right_unit = ""
        self.bottom_left_value = ""
        self.bottom_left_unit = ""
        self.center_scale = 1
        self.top_right_scale = 1.6
        self.top_left_scale = 1.4
        self.bottom_right_scale = 1.4
        self.bottom_left_scale = .65
        self.background_color = Color(0, 0, 0, 0)
        self.__dict__.update(kwargs)
        self.image = pygame.Surface([self.size, self.size], pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.icon_rect = self.rect.inflate(-self.padding, -self.padding)
        self.image.fill(self.unfilled_color, self.icon_rect)

    def set_icon(self, shape: WeatherShape, fill: float):
        """
        Sets the WeatherIcon's shape (image) and fill percentile

        :param shape: The WeatherShape
        :param fill: A decimal percentage of how much to fill the shape
        :returns: an instance of WeatherIcon
        """
        if self.shape != shape:
            self.shape = shape
            self.shape_file_name = self.shape.shape_to_image()
            self.dirty = 1

        fill = fill * FILL_TO_ANGLE
        if self.starting_angle != fill:
            self.starting_angle = fill
            self.dirty = 1

        return self

    def set_icon_information(self, shape: WeatherShape, fill: float, **kwargs):
        self.set_icon(shape, fill)
        self.__dict__.update(kwargs)
        self.dirty = 1
        return self

    def move(self, x: int = 0, y: int = 0):
        """
        Moves the WeatherIcon center to the x and y pos, x and y default to 0

        :param x: Desired center x position
        :param y: Desired center y position
        """
        if (x, y) != self.rect.center:
            self.rect.center = (x, y)
            self.icon_rect = self.rect.inflate(-self.padding, -self.padding)
            self.dirty = 1

    def resize(self, size, *args):
        """
        Resizes the WeatherIcon

        :param size: the new side length of the icon
        """
        if self.size != size:
            self.size = size
            self.dirty = 1

    def _return_text(self, value, unit, scale):
        """
        Returns a text surface and the surfaces rectangle for a drawn set of values and units
        "{value}{unit}"

        :param value:
        :param unit:
        :return:
        """
        AA_SCALING = 3
        WIDTH_PADDING = 1.2

        string = str()
        try:
            string = "%d%s" % (int(round(float(value))), unit)
        except TypeError and ValueError:
            string = f'{value}{unit}'

        if len(string) == 0:
            return pygame.Surface([1, 1]), pygame.Rect([(1, 1), (1, 1)])

        str_length_scaling = len(string) / 3
        text_size = AA_SCALING * get_text_size(
            round(((self.size - self.padding) / (scale * str_length_scaling * self.text_ratio))))
        font = pygame.font.SysFont('arial', text_size)
        textsurface = font.render(string, True, self.text_color)
        textsurface_rect = textsurface.get_rect()

        fnt = ImageFont.truetype(FONT, text_size)
        # create a pie image filled to the percentage
        pil_image = Image.new("RGBA",
                              (round(WIDTH_PADDING * textsurface_rect.width), round(textsurface_rect.height)))
        pil_draw = ImageDraw.Draw(pil_image)
        pil_draw.text((0, 0), string, font=fnt, fill=(self.text_color.r, self.text_color.g, self.text_color.b))
        # make 3 times smaller for AA like look
        pil_image = pil_image.resize((pil_image.width // AA_SCALING, pil_image.height // AA_SCALING),
                                     Image.ANTIALIAS)
        # convert pie image into PyGame image
        py_image = pil_to_pygame_image(pil_image)
        py_image_rect = py_image.get_rect()
        return py_image, py_image_rect

    def update(self):
        """
        Update redraws the image for the WeatherIcon only if the object has just been initialized or set_icon() has
        been called recently, AKA the weather icon is dirty.
        """
        if self.dirty == 1:
            print("Updating:", self, id(self))
            # delete the old image
            self.image = pygame.Surface([self.size, self.size], pygame.SRCALPHA)
            self.image.fill(self.background_color)
            new_rect = self.image.get_rect()
            new_rect.center = self.rect.center
            self.rect = new_rect
            self.icon_rect = self.rect.inflate(-self.padding, -self.padding)

            # create a pie image filled to the percentage
            pil_image = Image.new("RGBA", (self.size - self.padding, self.size - self.padding))
            pil_draw = ImageDraw.Draw(pil_image)
            pil_draw.pieslice((0, 0, self.size - self.padding, self.size - self.padding), self.ending_angle,
                              self.starting_angle,
                              fill=self.fill_color)
            # convert pie image into PyGame image
            py_image = pil_to_pygame_image(pil_image)
            py_image_rect = py_image.get_rect(center=self.image.get_rect().center)

            # create the icon image
            pil_icon_image = Image.open(self.shape.shape_to_image())
            pil_icon_image = pil_icon_image.resize(self.icon_rect.size, Image.ANTIALIAS)
            icon_image = pil_to_pygame_image(pil_icon_image)
            icon_image_rect = icon_image.get_rect(center=self.image.get_rect().center)

            # draw:
            self.image.fill(self.unfilled_color, icon_image_rect)
            self.image.blit(py_image, py_image_rect)
            self.image.blit(icon_image, icon_image_rect)

            # add text to center
            textsurface, textsurface_rect = self._return_text(self.center_value, self.center_unit, self.center_scale)
            textsurface_rect.center = self.image.get_rect().center
            self.image.blit(textsurface, textsurface_rect)
            # add text to upper right
            textsurface, textsurface_rect = self._return_text(self.top_right_value, self.top_right_unit,
                                                              self.top_right_scale)
            textsurface_rect.topright = self.image.get_rect().topright
            self.image.blit(textsurface, textsurface_rect)
            # add text to upper left
            textsurface, textsurface_rect = self._return_text(self.top_left_value, self.top_left_unit,
                                                              self.top_left_scale)
            textsurface_rect.topleft = self.image.get_rect().topleft
            self.image.blit(textsurface, textsurface_rect)
            # add text to upper right
            textsurface, textsurface_rect = self._return_text(self.bottom_right_value, self.bottom_right_unit,
                                                              self.bottom_right_scale)
            textsurface_rect.bottomright = self.image.get_rect().bottomright
            self.image.blit(textsurface, textsurface_rect)
            # add text to upper left
            textsurface, textsurface_rect = self._return_text(self.bottom_left_value, self.bottom_left_unit,
                                                              self.bottom_left_scale)
            textsurface_rect.bottomleft = self.image.get_rect().bottomleft
            self.image.blit(textsurface, textsurface_rect)


class SpriteGrid(DirtySprite):
    def __init__(self, *members, **kwargs):
        self.sprites = []
        super().__init__()
        for sprite in members:
            self.sprites.append(sprite)
        self.background_color = Color(0)
        self.width = 100
        self.height = 100
        self.padding = self.width / 25
        self.height_padding = 1
        self.labels = []
        self.text_color = Color(255, 255, 255, 255)
        self.spacing = 0
        self.image = pygame.Surface([self.width, self.height], pygame.SRCALPHA)
        self.image.fill(self.background_color)
        self.rect = self.image.get_rect()
        self.text_ratio = 7
        self.text_scale = 0.5
        self.__dict__.update(kwargs)
        self.grid_width = 0

    def move(self, x: int = 0, y: int = 0):
        """
        Moves the WeatherIcon center to the x amd y pos, x and y default to 0

        :param x: Desired center x position
        :param y: Desired center y position
        """
        if self.rect.center != (x, y):
            self.rect.center = (x, y)
            self.dirty = 1

    def replace_icons(self, array=None, *args):
        """
        Removes all old icons then adds the sprites listed in args

        :param array: a list of sprites to replace the current icons
        :param args: a place to individually add sprites which will be used to replace the sprites
        """
        # Clear the current list
        self.sprites = []
        # add sprite from list
        if array is not None:
            for sprite in array:
                self.sprites.append(sprite)
        # add sprites from args
        for sprite in args:
            self.sprites.append(sprite)
        self.dirty = 1

    def add_icon(self, sprite):
        """
        Adds a sprite to the grid layout.

        :param sprite:
        """
        if sprite not in self.sprites:
            self.sprites.append(sprite)
            self.dirty = 1

    def do_layout(self):
        """
        Lays out sprites based on sprite sizes and grid size.
        """
        old_center_location = self.rect.center

        # figure out the width of each grid
        grid_width = (self.width / len(self.sprites)) - self.padding
        if grid_width < 10:
            print("Grid Width calculation results in a non positive image width which is impossible, make width larger")
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
        self.height = new_height + self.height_padding

        # update image and rect
        self.image = pygame.Surface([self.width, self.height])
        self.rect = self.image.get_rect()
        self.rect.center = old_center_location

        self.grid_width = grid_width
        # set sprite locations
        for i, sprite in enumerate(self.sprites):
            sprite.rect.topleft = (
                i * grid_width + i * (1 + 1 / (len(self.sprites) - 1)) * self.padding, self.height_padding)

    def _return_text(self, string, scale):
        """
        Returns a text surface and the surfaces rectangle for a drawn string
        :param string:
        :param scale:
        :return:
        """
        AA_SCALING = 3
        PADDING_WIDTH = 1.3
        PADDING_HEIGHT = 1

        if len(string) == 0:
            return pygame.Surface([1, 1]), pygame.Rect([(1, 1), (1, 1)])

        str_length_scaling = 0.4
        proposed_text_size = round(
            ((self.width / len(self.sprites)) - self.padding) // ((str_length_scaling) * self.text_ratio) * scale)
        text_size = AA_SCALING * get_text_size(proposed_text_size)
        font = pygame.font.SysFont('arial', text_size)
        textsurface = font.render(string, True, self.text_color)
        textsurface_rect = textsurface.get_rect()

        fnt = ImageFont.truetype(FONT, text_size)
        # create a pie image filled to the percentage
        pil_image = Image.new("RGBA",
                              (round(PADDING_WIDTH * textsurface_rect.width),
                               round(PADDING_HEIGHT * textsurface_rect.height)))
        pil_draw = ImageDraw.Draw(pil_image)
        pil_draw.text((0, 0), string, font=fnt, fill=(self.text_color.r, self.text_color.g, self.text_color.b))
        # make 3 times smaller for AA like look
        pil_image = pil_image.resize((pil_image.width // AA_SCALING, pil_image.height // AA_SCALING),
                                     Image.ANTIALIAS)
        # convert pie image into PyGame image
        py_image = pil_to_pygame_image(pil_image)
        py_image_rect = py_image.get_rect()
        return py_image, py_image_rect

    def update(self):
        """
        Update redraws all of the sprites the SpriteGridContains if any are dirty.
        """
        if self.dirty == 1 or any(elem.dirty == 1 for elem in self.sprites):
            print("Updating:", self, id(self))

            # update layout
            self.do_layout()

            # update sprites
            for sprite in self.sprites:
                sprite.update()
                sprite.dirty = 0

            # draw sprites and labels
            for i, icon in enumerate(self.sprites):
                self.image.blit(icon.image, icon.rect)
                if i < len(self.labels):
                    if len(self.labels[i]) == 0:
                        continue
                    textsurface, textsurface_rect = self._return_text(self.labels[i], self.text_scale)
                    textsurface_rect.centerx = round((i + .5) * self.grid_width + (i + .5) * (
                            1 + 1 / (len(self.sprites) - 1)) * self.padding)  # round((i + .5) * self.spacing)
                    textsurface_rect.centery = self.height_padding // 2
                    self.image.blit(textsurface, textsurface_rect)


class TemperatureGraph(DirtySprite):
    # Properties
    def __init__(self, *members, **kwargs):
        super().__init__()
        self.num_of_graphs = 1
        self.temperatures = []
        self.background_color = Color(0, 0, 0, 255)
        self.line_colors = Color(255, 255, 255)
        self.dot_color = Color(0)
        self.width = 100
        self.height = 100
        self.antialiased = True
        self.thickness = 3
        self.unit = "°"
        self.text_color = Color(255, 255, 255)
        self.text_background_color = Color(100, 100, 100)
        self.padding = 12
        self.image = pygame.Surface([self.width, self.height], pygame.SRCALPHA)
        self.image.fill(self.background_color)
        self.rect = self.image.get_rect()
        self.__dict__.update(kwargs)

    def set_temperatures(self, *args):
        """
        Sets the graphs center_value values to the passed in args

        :param args: center_value values
        """
        # clear temperatures
        self.temperatures.clear()
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
        self.dirty = 1

    def _draw_lines(self, max_temp, min_temp, spacing, data, color):
        """
        Draws the lines for the weather graph

        :param max_temp: Maximum center_value of the graph
        :param min_temp: Minimum center_value of the graph
        :param spacing: the desired spacing between points
        :param data: the actual data to plot only the y values
        :param color:
        """
        circle_padding = 3
        font = pygame.font.SysFont('Arial', int(spacing // 8))

        # draw lines for center_value graph
        # generate point list based off of center_value values and sprite width
        point_list = []
        for x, temp in enumerate(data):
            point_list.append([x * spacing + spacing / 2,
                               variable_mapping(temp, min_temp, max_temp, self.height - self.padding, self.padding)])

        if self.antialiased:
            get_aalines_surface(self.image, point_list, self.thickness, color)
        else:
            draw.lines(self.image, color, False, point_list, self.thickness)

        # draw circles and center_value values
        for temp, point in zip(data, point_list):
            textsurface = font.render(f'{round(float(temp))}{self.unit}', True, self.text_color)
            textsurface_rect = textsurface.get_rect()
            textsurface_rect.center = point
            gfxdraw.aacircle(self.image, textsurface_rect.centerx, textsurface_rect.centery,
                             textsurface_rect.width // 2 + circle_padding,
                             self.text_background_color)
            gfxdraw.filled_circle(self.image, textsurface_rect.centerx, textsurface_rect.centery,
                                  textsurface_rect.width // 2 + circle_padding,
                                  self.text_background_color)
            self.image.blit(textsurface, textsurface_rect)

    def update(self):
        """
        Updates the graphics if the object has just been created or set_temperatures has been called
        """
        if self.dirty == 1:
            print("Updating:", self, id(self))

            # Clear old image
            self.image = pygame.Surface([self.width, self.height], pygame.SRCALPHA)
            self.image.fill(self.background_color)
            new_rect = self.image.get_rect()
            new_rect.center = self.rect.center
            self.rect = new_rect

            # draw new image
            max_temp = None
            min_temp = None
            temp_x_spacing = None
            if self.num_of_graphs > 1:
                for i in range(0, self.num_of_graphs):
                    # find max and min temperatures for y spacing
                    if max_temp is None or max(self.temperatures[i]) > max_temp:
                        max_temp = max(self.temperatures[i])
                    if min_temp is None or min(self.temperatures[i]) < min_temp:
                        min_temp = min(self.temperatures[i])

                # draw the lines
                for i in range(0, self.num_of_graphs):
                    temp_x_spacing = (self.width / len(self.temperatures[i]))
                    # create a point list for the temperatures
                    self._draw_lines(max_temp, min_temp, temp_x_spacing, self.temperatures[i], self.line_colors[i])

            else:
                # find max and min temperatures for y spacing
                max_temp = max(self.temperatures)
                min_temp = min(self.temperatures)
                temp_x_spacing = (self.width / len(self.temperatures))
                # draw the line
                self._draw_lines(max_temp, min_temp, temp_x_spacing, self.temperatures, self.line_colors)


class WeatherWidget(LayeredDirty):
    def __init__(self):
        sizing_small = WIDTH if WIDTH < HEIGHT else HEIGHT
        sizing_large = WIDTH if WIDTH > HEIGHT else HEIGHT
        self.center = 0.8
        # Create Widgets Dirty Sprites
        self.current_weather_icon = WeatherIcon(size=round(sizing_small / 10),
                                                padding=round(sizing_small / 75))
        self.hour_grid = SpriteGrid(width=sizing_small // 3, padding=round(sizing_small / 300),
                                    height_padding=round(sizing_small / 80))
        self.days_grid = SpriteGrid(width=sizing_small // 3, padding=round(sizing_small / 500),
                                    height_padding=round(sizing_small / 80))
        self.day_temperatures = TemperatureGraph(width=round(sizing_small / 2.7), height=sizing_large // 20,
                                                 line_colors=[self.current_weather_icon.fill_color,
                                                              self.current_weather_icon.text_color], num_of_graphs=2)

        self.clock_widget = ClockWidget(width=round(sizing_small / 7.5), height=round(sizing_small / 7.5),
                                        time_font_size=50, date_font_size=40,
                                        hour_color=tuple(self.current_weather_icon.unfilled_color),
                                        minute_color=self.current_weather_icon.fill_color)

        super().__init__(
            (self.current_weather_icon, self.hour_grid, self.days_grid, self.day_temperatures, self.clock_widget))
        # set icon locations
        self.current_weather_icon.move(int(self.center * WIDTH), int(0.05 * HEIGHT))
        self.hour_grid.move(int(self.center * WIDTH), int(0.12 * HEIGHT))
        self.days_grid.move(int(self.center * WIDTH), int(0.18 * HEIGHT))
        self.day_temperatures.move(int(self.center * WIDTH), int(0.24 * HEIGHT))
        self.clock_widget.move(int(WIDTH / 8), int(0.055 * HEIGHT))

        # create object surface and rectangle
        self.image = pygame.Surface([WIDTH, HEIGHT])
        self.rect = self.image.get_rect()

    def set_weather(self, weather_dict):
        """
        Sets the weather of all corresponding graphics

        :param weather_dict: weather dict created by WeatherAPI
        """
        # Current Weather icon update
        self.current_weather_icon.set_icon_information(shape=weather_dict['current']['shape'],
                                                       fill=weather_dict['current']['fill%'],
                                                       center_value=weather_dict['current']['temperature'],
                                                       center_unit="°",
                                                       top_right_value=weather_dict['current']['value'],
                                                       top_right_unit=weather_dict['current']['unit'],
                                                       bottom_left_value=f"Feel: {round(weather_dict['current']['feels'])}°")

        # Update the Hour Grid
        hour_labels = []
        hour_icons = []
        for i in range(5):
            hour_icons.append(
                WeatherIcon().set_icon_information(shape=weather_dict['hourly'][i]['shape'],
                                                   fill=weather_dict['hourly'][i]['fill%'],
                                                   center_value=weather_dict['hourly'][i]['temperature'],
                                                   center_unit="°",
                                                   top_right_value=weather_dict['hourly'][i]['value'],
                                                   top_right_unit=weather_dict['hourly'][i]['unit']))
            hour_labels.append(weather_dict['hourly'][i]['time'])
        self.hour_grid.replace_icons(hour_icons)
        self.hour_grid.labels = hour_labels

        # Update the Day Grid
        day_labels = []
        day_icons = []
        for i in range(6):
            day_icons.append(WeatherIcon().set_icon_information(shape=weather_dict['forecast'][i]['shape'],
                                                                fill=weather_dict['forecast'][i]['fill%'],
                                                                center_value=weather_dict['forecast'][i][
                                                                    'value'],
                                                                center_unit=weather_dict['forecast'][i][
                                                                    'unit']))
            day_labels.append(weather_dict['forecast'][i]['time'])
        self.days_grid.replace_icons(day_icons)
        self.days_grid.labels = day_labels

        # Update the Day Temperatures Graph
        # TODO: Refactor for easier editing/readability
        self.day_temperatures.set_temperatures([weather_dict['forecast'][0]['highTemperature'],
                                                weather_dict['forecast'][1]['highTemperature'],
                                                weather_dict['forecast'][2]['highTemperature'],
                                                weather_dict['forecast'][3]['highTemperature'],
                                                weather_dict['forecast'][4]['highTemperature'],
                                                weather_dict['forecast'][5]['highTemperature']],
                                               [weather_dict['forecast'][0]['lowTemperature'],
                                                weather_dict['forecast'][1]['lowTemperature'],
                                                weather_dict['forecast'][2]['lowTemperature'],
                                                weather_dict['forecast'][3]['lowTemperature'],
                                                weather_dict['forecast'][4]['lowTemperature'],
                                                weather_dict['forecast'][5]['lowTemperature']])


class ClockWidget(DirtySprite):
    def __init__(self, **kwargs):
        super().__init__()
        self.time = datetime.fromtimestamp(time.time()).strftime('%I:%M %p')
        self.date = datetime.fromtimestamp(time.time()).strftime('%A, %b %d')
        self.background_color = Color(0)
        self.width = 100
        self.height = 100
        self.image = pygame.Surface([self.width, self.height], pygame.SRCALPHA)
        self.text_padding = 10
        self.image.fill(self.background_color)
        self.rect = self.image.get_rect()
        self.text_color = Color(255, 255, 255)
        self.hour_color = (0, 255, 0)
        self.minute_color = (0, 0, 255)
        self.time_font_size = 100
        self.date_font_size = 100
        self.__dict__.update(kwargs)
        self.dirty = 1

    def move(self, x: int = 0, y: int = 0):
        """
        Moves the WeatherIcon center to the x and y pos, x and y default to 0

        :param x: Desired center x position
        :param y: Desired center y position
        """
        if (x, y) != self.rect.center:
            self.rect.center = (x, y)
            self.dirty = 1

    def checkTime(self):
        self.dirty = 1

    def _return_text(self, string, text_size):
        AA_SCALING = 3

        fnt = ImageFont.truetype(FONT, text_size)
        # create a pie image filled to the percentage
        pil_image = Image.new("RGBA", (round(AA_SCALING * self.width), round(AA_SCALING * self.height / 2)))
        pil_draw = ImageDraw.Draw(pil_image)
        w, h = pil_draw.textsize(string, font=fnt)
        pil_draw.text(((round(AA_SCALING * self.width) - w) // 2, (round(AA_SCALING * self.height / 2) - h) // 2),
                      string, font=fnt, fill=(self.text_color.r, self.text_color.g, self.text_color.b))
        # make 3 times smaller for AA like look
        pil_image = pil_image.resize((self.width, round(self.height / 2)), Image.ANTIALIAS)
        # convert pie image into PyGame image
        py_image = pil_to_pygame_image(pil_image)
        return py_image, py_image.get_rect()

    def update(self):
        if self.dirty == 1:
            # print(self)
            # Clear old image
            self.image = pygame.Surface([self.width, self.height], pygame.SRCALPHA)
            self.image.fill(self.background_color)
            new_rect = self.image.get_rect()
            new_rect.center = self.rect.center
            self.rect = new_rect

            # Update date and time
            self.time = datetime.fromtimestamp(time.time()).strftime('%I:%M %p')
            self.date = datetime.fromtimestamp(time.time()).strftime('%A, %b %d')

            # Draw and blit text
            textsurface, textsurface_rect = self._return_text(self.time, self.time_font_size)
            textsurface_rect.centerx = self.image.get_rect().centerx
            textsurface_rect.centery = self.image.get_rect().centery - self.text_padding
            self.image.blit(textsurface, textsurface_rect)
            textsurface, textsurface_rect = self._return_text(self.date, self.date_font_size)
            textsurface_rect.centerx = self.image.get_rect().centerx
            textsurface_rect.centery = self.image.get_rect().centery + self.text_padding
            self.image.blit(textsurface, textsurface_rect)

            # Draw an ellipse of diameter width and height for the hour
            ellipse_image = draw_arc(self.width, self.height,
                                     variable_mapping(float(self.time[:2]), 0.0, 12.0, 0.0, 1.0), 4, self.hour_color)
            ellipse_image_rect = ellipse_image.get_rect()
            ellipse_image_rect.center = self.image.get_rect().center
            self.image.blit(ellipse_image, ellipse_image_rect)
            # Draw second elllipse
            ellipse_image = draw_arc(round(self.width - 16), round(self.height - 16),
                                     variable_mapping(float(datetime.fromtimestamp(time.time()).strftime('%S')[:2]),
                                                      0.0, 60.0, 0.0, 1.0), 4, self.hour_color)
            ellipse_image_rect = ellipse_image.get_rect()
            ellipse_image_rect.center = self.image.get_rect().center
            self.image.blit(ellipse_image, ellipse_image_rect)
            # Draw Minute ellipse
            ellipse_image = draw_arc(round(self.width - 8), round(self.height - 8),
                                     variable_mapping(float(datetime.fromtimestamp(time.time()).strftime('%M')[:2]),
                                                      0.0, 60.0, 0.0, 1.0), 4, self.minute_color)
            ellipse_image_rect = ellipse_image.get_rect()
            ellipse_image_rect.center = self.image.get_rect().center
            self.image.blit(ellipse_image, ellipse_image_rect)


if __name__ == "__main__":
    pass
