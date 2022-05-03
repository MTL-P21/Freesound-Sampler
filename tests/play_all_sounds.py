import keyboard
import pygame

import os

path = os.path.normpath(os.getcwd() + os.sep + os.pardir + "/data")
pygame.init()
pygame.mixer.init()

for filename in os.listdir(path):
    if filename.endswith(".mp3"):
        file = os.path.normpath(os.getcwd() + os.sep + os.pardir + os.sep + "data" + os.sep + filename)
        print(file)
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():

            pygame.time.Clock().tick(10)