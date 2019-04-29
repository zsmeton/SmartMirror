import pygame

pygame.mixer.init(8000, -16, 2, 1024*4)
pygame.display.set_mode((200,100))

class Speaker:
    volume = 1.0
    def __init__(self,audioFile):
        self.audioFile = audioFile

    # change the playback file 
    def changeAudio(self,filename):
        self.audioFile = filename

    def setVolume(self, volume):
        self.volume = volume

    # increase volume 
    def volumeUp(self):
        self.volume += 0.05
        if self.volume > 1.0:
            print("Max volume reached.")
            self.volume = 1.0
        pygame.mixer.music.set_volume(self.volume)
                
    # decrease volume
    def volumeDown(self):
        try:
            self.volume -= 0.05
            if self.volume < 0.0:
                raise ValueError
        except ValueError:
            print("Min volume reached.")
            self.volume = 0.0
        pygame.mixer.music.set_volume(self.volume)

    # play audio file 
    def play(self):
        pygame.mixer.music.load(self.audioFile)
        pygame.mixer.music.play(0)
        






    
