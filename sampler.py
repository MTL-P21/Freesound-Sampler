import keyboard
import pygame
import os

path = os.path.normpath(os.getcwd() + os.sep + os.pardir + "/data")
files = []
files.append(os.path.normpath(os.getcwd() + os.sep + "data" + os.sep + "Airy Watery Trumpet.wav.mp3"))
files.append(os.path.normpath(os.getcwd() + os.sep + "data" + os.sep + "Party Pack, Horn Coil 01, Long, 01.wav.mp3"))
files.append(os.path.normpath(os.getcwd() + os.sep + "data" + os.sep + "TrumpetValves_1.wav.mp3"))
files.append(os.path.normpath(os.getcwd() + os.sep + "data" + os.sep + "TrumpetValves_2.wav.mp3"))
files.append(os.path.normpath(os.getcwd() + os.sep + "data" + os.sep + "TrumpetValves_5.wav.mp3"))
files.append(os.path.normpath(os.getcwd() + os.sep + "data" + os.sep + "TrumpetValves_6.wav.mp3"))

pygame.init()
pygame.mixer.init()

key_pressed = False

def play_music(filename):
  pygame.mixer.music.load(filename)
  pygame.mixer.music.play()

while True:
    if keyboard.is_pressed("q") and not key_pressed:
        play_music(files[0])
        key_pressed = True
        print("True press")
    if keyboard.is_pressed("w") and not key_pressed:
        play_music(files[1])
        key_pressed = True
        print("True press")
    if keyboard.is_pressed("e") and not key_pressed:
        play_music(files[2])
        key_pressed = True
        print("True press")
    if keyboard.is_pressed("r") and not key_pressed:
        play_music(files[3])
        key_pressed = True
        print("True press")
    if keyboard.is_pressed("t") and not key_pressed:
        play_music(files[4])
        key_pressed = True
        print("True press")
    else:
        key_pressed = False
        print("False press")