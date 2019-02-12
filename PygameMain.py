import json
from enum import Enum

import pygame
from pygame import Surface, Color
from pygame.sprite import LayeredDirty

# CONSTANTS
import GUI
from WeatherJSON import weather_hook

MAX_FRAME_RATE = 60
WIDTH = 400
HEIGHT = 300
BACKGROUND_COLOR = Color(0)


# EVENT TIMERS
class EventTimers(Enum):
    GET_WEATHER = 60000


class SmartMirrorApp:
    weather_file = "weather.txt"
    weather = None
    widgets = []
    # creates a clock
    clock = pygame.time.Clock()

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.done = False

        # Create Background Surface
        self.background = Surface(self.screen.get_size())
        Surface.fill(self.background, BACKGROUND_COLOR)

        # Create Dirty Sprites
        self.current_weather_icon = GUI.WeatherIcon()
        # Create Layered Dirty
        self.my_sprites = LayeredDirty()
        # Can Add Spites to LayeredDirty using:
        self.my_sprites.add(self.current_weather_icon)
        self.my_sprites.clear(self.screen, self.background)

        # TODO: Remove test
        with open(self.weather_file, 'r') as fin:
            self.weather = json.load(fin, object_hook=weather_hook)
        self.current_weather_icon.set_icon(shape=self.weather['current']['shape'],
                                           fill=self.weather['current']['fill%'])
        # TODO: test end
        # Set event timers
        #self.set_timers()
        # add events to queue
        #pygame.event.post(EventTimers.GET_WEATHER.name)


    def set_timers(self):
        """
        Sets event timers for all members of the EventTimers class
        """
        for event in EventTimers:
            pygame.time.set_timer(event.name, event.value)

    def handle_events(self):
        """
        Runs the logic for event processing
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.done = True
            elif event.type == EventTimers.GET_WEATHER.name:
                with open(self.weather_file, 'r') as fin:
                    self.weather = json.load(fin, object_hook=weather_hook)
                self.current_weather_icon.set_icon(shape=self.weather['current']['shape'], fill=self.weather['current']['fill%'])

    def loop(self):
        while not self.done:
            self.handle_events()

            # Update spites
            self.my_sprites.update()
            rects = self.my_sprites.draw(self.screen)

            # draw non sprites

            # draw display
            self.clock.tick(MAX_FRAME_RATE)
            pygame.display.update(rects)


if __name__ == "__main__":
    app = SmartMirrorApp()
    app.loop()
