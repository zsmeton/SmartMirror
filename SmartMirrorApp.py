import json

from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.lang import Builder
from kivy.properties import StringProperty, ReferenceListProperty, NumericProperty, ObjectProperty
from kivy.uix.screenmanager import Screen, NoTransition, ScreenManager
from kivy.uix.widget import Widget

from Updateable import Updateable
from WeatherJSON import weather_hook
from WeatherShape import WeatherShape

# Set Kivy App configurations
Config.set('graphics', 'fullscreen', 'auto')  # Sets window to fullscreen
Config.set('graphics', 'multisamples', '8')  # Sets window to fullscreen
Config.write()
Builder.load_file('SmartMirror.kv')

# Update Times
WEATHER_UPDATE = 1.0 / 60.0
DEFAULT_UPDATE = 1.0 / 60.0
FILL_TO_ANGLE = 360


# Widgets #
class LoadingIcon(Widget):
    # Properties
    inner_color = (255, 255, 255)
    other_color = (0, 0, 0)
    starting_angle = NumericProperty(0)
    ending_angle = NumericProperty(0)
    size_x = NumericProperty(100)
    size_y = NumericProperty(100)
    size = ReferenceListProperty(size_x, size_y)
    thickness = NumericProperty(5)

    def __init__(self, **kwargs):
        super().__init__()
        self.__dict__.update(kwargs)

    def update(self, dt=None):
        if self.starting_angle // 360 == 0:
            self.starting_angle += 2
            self.ending_angle += 1
        elif self.ending_angle != self.starting_angle:
            self.ending_angle += 2
            self.ending_angle += 1
        else:
            self.ending_angle = 0
            self.starting_angle = 0


# TODO: create weather icon widget
class WeatherIcon(Widget):
    # Properties
    fill_color = (255, 255, 255)
    other_color = (0, 0, 0)
    starting_angle = NumericProperty(0)
    ending_angle = NumericProperty(0)
    size_x = NumericProperty(100)
    size_y = NumericProperty(100)
    size = ReferenceListProperty(size_x, size_y)
    shape = WeatherShape.SUN
    file_name = shape.shape_to_image()
    image = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__()
        self.__dict__.update(kwargs)

    def update(self, shape, fill, dt=None):
        self.ending_angle = fill * FILL_TO_ANGLE
        self.shape = shape
        self.file_name = self.shape.shape_to_image()
        self.image.source = self.file_name


# TODO: Add Weather Display Widget
class WeatherDisplay(Widget, Updateable):
    # Properties
    # dictionary of weather data
    weather = None
    # location of weather data stream
    weather_file = "weather.txt"
    # add WeatherIcon widgets
    current_icon = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__()
        self.__dict__.update(kwargs)

    def update(self, dt=None):
        with open(self.weather_file, 'r') as fin:
            self.weather = json.load(fin, object_hook=weather_hook)
        self.current_icon.update(shape=self.weather['current']['shape'], fill=self.weather['current']['fill%'])
        print(self.current_icon.pos)
        print(self.center)


# TODO: Add Calendar Display Widget
class CalendarDisplay(Widget):
    pass


# Screens #

# TODO: Develop Sleep Screen logic
class SleepScreen(Screen):
    name = StringProperty('sleep')
    pass


# TODO: Develop Main Screen
class MainScreen(Screen):
    name = StringProperty('main')
    # Create loading widget
    loading_icon = LoadingIcon(thickness=2, outer_color=(0, 0, 255))
    # create weather widget
    weather_widget = ObjectProperty(None)

    # create animation list
    # updateable_widgets = [loading_icon]

    # # Create identification process
    # queue = Queue()
    # recognizer = FaceRecognizer
    # process = Process(target=recognizer.update, args=(('unknown.py', queue)))

    def __init__(self, **kw):
        super().__init__(**kw)
        # Schedule base update
        Clock.schedule_interval(self.update, DEFAULT_UPDATE)
        # schedule special updates
        Clock.schedule_interval(self.weather_widget.update, WEATHER_UPDATE)
        # Add Widgets
        self.add_widget(self.loading_icon)

    def update(self, dt=None):
        # Animate all children
        self.loading_icon.update()

        # # Check processes
        # if not self.process.is_alive():
        #     self.remove_widget(self.loading_icon)
        #     self.process.join()
        #     if not self.introduction_label.parent:
        #         self.introduction_label.text = self.queue.get()
        #         self.add_widget(self.introduction_label)


# TODO: Develop Calendar Screen
class CalendarScreen(Screen):
    name = StringProperty('calendar')
    pass


# TODO: Develop Weather Screen
class WeatherScreen(Screen):
    name = StringProperty('weather')
    pass


#   Application #
class SmartMirrorApp(App):
    def build(self):
        sm = ScreenManager(transition=NoTransition())
        main = MainScreen()
        sleep = SleepScreen()
        calendar = CalendarScreen()
        weather = WeatherScreen()
        sm.add_widget(main)
        sm.add_widget(sleep)
        sm.add_widget(calendar)
        sm.add_widget(weather)
        sm.current = 'main'
        return sm


if __name__ == '__main__':
    SmartMirrorApp().run()
