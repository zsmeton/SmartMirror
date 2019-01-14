from kivy.app import App
from kivy.config import Config
Config.set('graphics', 'fullscreen', 'auto')


from kivy.uix.widget import Widget

### Set Kivy App configurations


class MirrorDisplay(Widget):
    temp = 1


class SmartMirrorApp(App):
    def build(self):
        return MirrorDisplay()


if __name__ == '__main__':
    SmartMirrorApp().run()
