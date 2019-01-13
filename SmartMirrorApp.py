from kivy.app import App
from kivy.uix.widget import Widget


class MirrorDisplay(Widget):
    temp = 1


class SmartMirrorApp(App):
    def build(self):
        return MirrorDisplay()


if __name__ == '__main__':
    SmartMirrorApp().run()
