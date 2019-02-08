import pygame
from pygame.sprite import DirtySprite
from pygame import gfxdraw


# TODO: Implement WeatherIcon
class WeatherIcon(DirtySprite):
    def __init__(self, *groups):
        super().__init__(*groups)

    def update(self, *args):
        super().update(*args)