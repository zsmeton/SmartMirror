from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.lang import Builder

# Set Kivy App configurations
Config.set('graphics', 'fullscreen', 'auto')  # Sets window to fullscreen
Config.set('graphics', 'multisamples', '8')  # Sets window to fullscreen
Config.write()

Builder.load_file('SmartMirror.kv')


# Widget that creates a small loading screen while other processes run
class LoadingCircle(Widget):
    starting_angle = NumericProperty(0)
    ending_angle = NumericProperty(0)
    size_x = NumericProperty(100)
    size_y = NumericProperty(100)
    size = ReferenceListProperty(size_x, size_y)
    thickness = NumericProperty(10)
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


class LoadingScreen(Screen):
    loadCircle = ObjectProperty(None)
    pass


class SettingsScreen(Screen):
    pass




class SmartMirrorApp(App):
    def build(self):
        # Create the screen manager
        sm = ScreenManager()
        loader = LoadingScreen(name='menu')
        Clock.schedule_interval(loader.loadCircle.update, 1.0 / 60.0)
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(loader)

        return sm


if __name__ == '__main__':
    SmartMirrorApp().run()
