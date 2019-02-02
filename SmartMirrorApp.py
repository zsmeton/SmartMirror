from multiprocessing import Process, Queue

from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.lang import Builder
from kivy.properties import StringProperty, ReferenceListProperty, NumericProperty
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, NoTransition, ScreenManager
from kivy.uix.widget import Widget

from FacialRecognition import FaceRecognizer

# Set Kivy App configurations
Config.set('graphics', 'fullscreen', 'auto')  # Sets window to fullscreen
Config.set('graphics', 'multisamples', '8')  # Sets window to fullscreen
Config.write()
Builder.load_file('SmartMirror.kv')


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
        super().__init__(**kwargs)

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

# TODO: Add process subclass

# TODO: Add Weather Display Widget
class WeatherDisplay(Widget):
    pass


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
    loading_icon = LoadingIcon()
    loading_icon.thickness = 2
    loading_icon.outer_color = (0, 0, 255)
    # Create introduction widget
    introduction_label = Label(text='Loading Finished')
    # Create identification process
    queue = Queue()
    recognizer = FaceRecognizer
    process = Process(target=recognizer.update, args=('unknown.py', queue, ))

    def __init__(self, **kw):
        super().__init__(**kw)
        # Schedule base update
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        # Add Widgets
        self.add_widget(self.loading_icon)
        self.process.start()

    def update(self, dt=None):
        # Animate all children
        for child in self.children:
            try:
                child.update()
            except AttributeError:
                pass

        # Check processes
        if not self.process.is_alive():
            self.remove_widget(self.loading_icon)
            self.process.join()
            if not self.introduction_label.parent:
                self.introduction_label.text = self.queue.get()
                self.add_widget(self.introduction_label)


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
        return sm


if __name__ == '__main__':
    SmartMirrorApp().run()
