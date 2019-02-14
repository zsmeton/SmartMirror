import json
from enum import Enum

import pygame
from pygame import Surface, Color, USEREVENT
from pygame.sprite import LayeredDirty

# CONSTANTS
from GUI import WeatherWidget
from WeatherJSON import weather_hook
from Display import WIDTH, HEIGHT, MAX_FRAME_RATE

BACKGROUND_COLOR = Color(0)


# EVENT TIMERS
class EventTimers(Enum):
    GET_WEATHER = 30000

    def get_event(self):
        events = {self.GET_WEATHER: USEREVENT + 1}
        return events.get(self)


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
        self.weather_widget = WeatherWidget()

        # Create Layered Dirty
        self.my_sprites = LayeredDirty()
        # Can Add Spites to LayeredDirty using:
        self.my_sprites.add(self.weather_widget)
        self.my_sprites.clear(self.screen, self.background)

        # Set event timers
        self.set_timers()
        # add events to queue
        for event in EventTimers:
            my_event = pygame.event.Event(event.get_event())
            pygame.event.post(my_event)

    def set_timers(self):
        """
        Sets event timers for all members of the EventTimers class
        """
        for event in EventTimers:
            pygame.time.set_timer(event.get_event(), event.value)

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
            elif event.type == EventTimers.GET_WEATHER.get_event():
                with open(self.weather_file, 'r') as fin:
                    self.weather = json.load(fin, object_hook=weather_hook)
                self.weather_widget.set_weather(self.weather)

    def loop(self):
        """
        The game drawing loop which is called until an Exit Event is created
        """
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
