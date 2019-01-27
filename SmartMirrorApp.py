import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.lang import Builder
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget

from FacialRecognition import FaceRecognizer

# Set Kivy App configurations
Config.set('graphics', 'fullscreen', 'auto')  # Sets window to fullscreen
Config.set('graphics', 'multisamples', '8')  # Sets window to fullscreen
Config.write()

Builder.load_file('SmartMirror.kv')

""" Non-Display functions """


# Author: @ApplePie420
# https://github.com/ApplePie420/OWMapp
def weather_image(description):
    source_img = "error.png"
    if description == "broken clouds":
        source_img = "weather/broken-clouds.png"
    elif description == "cloudy":
        source_img = "weather/overcast clouds.png"
    elif description == "cold":
        source_img = "weather/cold.png"
    elif description == "light intensity shower rain":
        source_img = "weather/drop.png"
    elif description == "shower rain":
        source_img = "weather/drop.png"
    elif description == "heavy intensity shower rain":
        source_img = "weather/drop.png"
    elif description == "shower rain":
        source_img = "weather/drop.png"
    elif description == "ragged shower rain":
        source_img = "weather/drop.png"
    elif description == "extreme rain":
        source_img = "weather/flood.png"
    elif description == "smoke":
        source_img = "weather/fog.png"
    elif description == "haze":
        source_img = "weather/fog.png"
    elif description == "fog":
        source_img = "weather/fog.png"
    elif description == "sand":
        source_img = "weather/fog.png"
    elif description == "dust":
        source_img = "weather/fog.png"
    elif description == "volcanic ash":
        source_img = "weather/fog.png"
    elif description == "squalls":
        source_img = "weather/fog.png"
    elif description == "mist":
        source_img = "weather/foggy.png"
    elif description == "hot":
        source_img = "weather/hot.png"
    elif description == "light rain":
        source_img = "weather/light-rain.png"
    elif description == "light snow":
        source_img = "weather/light-snow.png"
    elif description == "light wind":
        source_img = "weather/light-wind.png"
    elif description == "few clouds":
        source_img = "weather/partialy-cloudy.png"
    elif description == "scattered clouds":
        source_img = "weather/partialy-cloudy.png"
    elif description == "moderate rain":
        source_img = "weather/rain.png"
    elif description == "heavy intensity rain":
        source_img = "weather/rain.png"
    elif description == "very heavy rain":
        source_img = "weather/rain.png"
    elif description == "sleet":
        source_img = "weather/sleet.png"
    elif description == "shower sleet":
        source_img = "weather/sleet.png"
    elif description == "snow":
        source_img = "weather/snowing.png"
    elif description == "heavy snow":
        source_img = "weather/snowing.png"
    elif description == "light rain and snow":
        source_img = "weather/snowing.png"
    elif description == "rain and snow":
        source_img = "weather/snowing.png"
    elif description == "light shower snow":
        source_img = "weather/snowing.png"
    elif description == "shower snow":
        source_img = "weather/snowing.png"
    elif description == "heavy shower snow":
        source_img = "weather/snowing.png"
    elif description == "storm":
        source_img = "weather/storm.png"
    elif description == "violent storm":
        source_img = "weather/storm.png"
    elif description == "thunderstorm with light rain":
        source_img = "weather/storm.png"
    elif description == "thunderstorm with rain":
        source_img = "weather/storm.png"
    elif description == "light thunderstorm":
        source_img = "weather/storm.png"
    elif description == "thunderstorm":
        source_img = "weather/storm.png"
    elif description == "heavy thunderstorm":
        source_img = "weather/storm.png"
    elif description == "ragged thunderstorm":
        source_img = "weather/storm.png"
    elif description == "thunderstorm with light drizzle":
        source_img = "weather/storm.png"
    elif description == "thunderstorm with drizzle":
        source_img = "weather/storm.png"
    elif description == "thunderstorm with heavy drizzle":
        source_img = "weather/storm.png"
    elif description == "clear sky":
        source_img = "weather/sunny.png"
    elif description == "calm":
        source_img = "weather/sunny.png"
    elif description == "high wind, near gale":
        source_img = "weather/wind.png"
    elif description == "gale":
        source_img = "weather/wind.png"
    elif description == "severe gale":
        source_img = "weather/wind.png"
    elif description == "light breeze":
        source_img = "weather/wind.png"
    elif description == "gentle breeze":
        source_img = "weather/wind.png"
    elif description == "moderate breeze":
        source_img = "weather/wind.png"
    elif description == "fresh breeze":
        source_img = "weather/wind.png"
    elif description == "strong breeze":
        source_img = "weather/wind.png"

    return source_img


class RecognitionThread(threading.Thread):
    def __init__(self, thread_id: int, name: str, fileName: str, instance: FaceRecognizer):
        """
        Creates a new thread to run facial recognition on the file "unknown.png"

        :param thread_id:
        :param name: A name to identify the thread
        """
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = name
        self.instance = instance
        self.fileName = fileName

    def run(self):
        """
        Called when the thread method start() is called, runs the function being threaded
        """
        print("Starting " + self.name)
        self.instance.update(unknown_file_name=self.fileName)
        print("Exiting " + self.name)


""" Widgets """


class DailyWeather(Widget):
    pass


class WeatherForecast(Widget):
    pass


# Widget that creates a small loading screen while other processes run
class LoadingCircle(Widget):
    starting_angle = NumericProperty(0)
    ending_angle = NumericProperty(0)
    size_x = NumericProperty(400)
    size_y = NumericProperty(400)
    size = ReferenceListProperty(size_x, size_y)
    thickness = NumericProperty(5)
    color_r = 0
    color_g = 230
    color_b = 255

    def update(self, dt):
        if self.starting_angle // 360 == 0:
            self.starting_angle += 2
            self.ending_angle += 1
        elif self.ending_angle != self.starting_angle:
            self.ending_angle += 2
            self.ending_angle += 1
        else:
            self.ending_angle = 0
            self.starting_angle = 0


""" Screens """


class LoadingScreen(Screen):
    # Properties
    loadCircle = ObjectProperty(None)

    def __init__(self, thread, **kw):
        super().__init__(**kw)
        self.thread = thread

    def start_thread(self):
        if not self.thread.is_alive():
            self.thread.start()

    def check_thread(self, dt):
        if self.thread.isAlive():
            print("Thread (", self.thread.name, ") is running", sep="")
        else:
            print("Thread (", self.thread.name, ") has not started", sep="")


class MainScreen(Screen):
    pass


""" App """


class SmartMirrorApp(App):
    def build(self):
        # Create threads:
        recognizer = FaceRecognizer(enc_location='known_faces', name_conv_location='pictureNames.conv')
        face_thread = RecognitionThread(thread_id=1, name="Face_Thread", fileName="unknown.png", instance=recognizer)

        # Create the screen manager:
        sm = ScreenManager()

        # Create the screens
        face_loader = LoadingScreen(name='recognition_loading', thread=face_thread)
        main = MainScreen(name='main')

        # schedule functions
        Clock.schedule_interval(face_loader.loadCircle.update, 1.0 / 60.0)
        Clock.schedule_interval(face_loader.check_thread, 1.0 / 20.0)

        # add screens to screen manager
        sm.add_widget(main)
        sm.add_widget(face_loader)
        return sm


if __name__ == '__main__':
    SmartMirrorApp().run()
