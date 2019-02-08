import pygame
from pygame import Surface, Color
from pygame.sprite import LayeredDirty

# CONSTANTS
MAX_FRAME_RATE = 60
WIDTH = 400
HEIGHT = 300
BACKGROUND_COLOR = Color(0)


class SmartMirrorApp:
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

        # Create Layered Dirty
        self.my_sprites = LayeredDirty()
        # Can Add Spites to LayeredDirty using:
        # self.my_sprites.add()
        self.my_sprites.clear(self.screen, self.background)

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
