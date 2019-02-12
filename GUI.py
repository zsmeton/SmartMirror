import pygame
from PIL import Image, ImageDraw
from pygame import Color, draw
from pygame.sprite import DirtySprite

# Constants
FILL_TO_ANGLE = 360


def PIL_to_PyGame_image(pil_image):
    mode = pil_image.mode
    size = pil_image.size
    data = pil_image.tobytes()
    image = pygame.image.fromstring(data, size, mode)
    return image


# TODO: Implement WeatherIcon
class WeatherIcon(DirtySprite):
    # Properties
    fill_color = (51, 255, 255)
    unfilled_color = Color(100, 100, 100)
    shape_file_name = ""
    starting_angle = 0
    ending_angle = 0
    diameter = 100

    def __init__(self, *groups, **kwargs):
        super().__init__(*groups)
        self.__dict__.update(kwargs)
        self.image = pygame.Surface([self.diameter, self.diameter])
        self.image.fill(self.unfilled_color)
        self.rect = self.image.get_rect()

    def set_icon(self, shape, fill):
        self.shape_file_name = shape.shape_to_image()
        self.ending_angle = FILL_TO_ANGLE - fill * FILL_TO_ANGLE
        self.dirty = 1

    def update(self):
        # create a rectangle the size of the sprites rectangle
        draw.rect(self.image, self.unfilled_color, self.rect)

        # create a pie image filled to the percentage
        pil_image = Image.new("RGBA", (self.diameter, self.diameter))
        pil_draw = ImageDraw.Draw(pil_image)
        pil_draw.pieslice((0, 0, self.diameter, self.diameter), self.ending_angle, self.starting_angle,
                          fill=self.fill_color)

        # convert pie image into PyGame image

        py_image = PIL_to_PyGame_image(pil_image)
        py_image_rect = py_image.get_rect(center=self.image.get_rect().center)
        self.image.blit(py_image, py_image_rect)

        # add icon to the rectangle
        pil_icon_image = Image.open(self.shape_file_name)
        pil_icon_image = pil_icon_image.resize(self.rect.size)
        icon_image = PIL_to_PyGame_image(pil_icon_image)
        icon_image_rect = icon_image.get_rect(center=self.image.get_rect().center)
        self.image.blit(icon_image, icon_image_rect)
