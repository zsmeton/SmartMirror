import json
from enum import Enum

import pygame
from pygame import Surface, Color, USEREVENT

from Display import WIDTH, HEIGHT, MAX_FRAME_RATE
from FileSettings import WEATHER_FILE
from GUI import WeatherWidget
from WeatherJSON import weather_hook

# CONSTANTS
BACKGROUND_COLOR = Color(0)


# EVENT TIMERS
class EventTimer(Enum):
    GET_WEATHER = 30000
    GET_TIME = 100

    def get_event(self):
        """
        Returns the event integer for the specified EvenTimer
        :return: pygame event integer
        """
        events = {self.GET_WEATHER: USEREVENT + 1, self.GET_TIME: USEREVENT + 2}
        return events.get(self)


class SmartMirrorApp:
    weather_file = WEATHER_FILE
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
        self.background.fill(BACKGROUND_COLOR)

        # Create Dirty Sprites
        self.weather_widget = WeatherWidget()

        self.weather_widget.clear(self.screen, self.background)

        # Set event timers
        self.set_timers()
        # add events to queue
        for event in EventTimer:
            my_event = pygame.event.Event(event.get_event())
            pygame.event.post(my_event)

    @staticmethod
    def set_timers():
        """
        Sets event timers for all members of the EventTimer class
        """
        for event in EventTimer:
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
            elif event.type == EventTimer.GET_WEATHER.get_event():
                self.background.fill(BACKGROUND_COLOR)
                self.weather_widget.clear(self.screen, self.background)
                self.weather_widget = WeatherWidget()
                self.weather_widget.clear(self.screen, self.background)
                with open(self.weather_file, 'r') as fin:
                    self.weather = json.load(fin, object_hook=weather_hook)
                    print("Re-pulling weather data")
                self.weather_widget.set_weather(self.weather)
                self.weather_widget.update()
            elif event.type == EventTimer.GET_TIME.get_event():
                self.weather_widget.clock_widget.checkTime()

    def loop(self):
        """
        The game drawing loop which is called until an Exit Event is created
        """
        while not self.done:
            self.handle_events()

            # Update spites
            self.weather_widget.update()

            rects = self.weather_widget.draw(self.screen)
            pygame.display.update(rects)
            # draw non sprites

            # draw display
            self.clock.tick(MAX_FRAME_RATE)
        pygame.quit()


if __name__ == "__main__":
    app = SmartMirrorApp()
    app.loop()
