#!/usr/bin/env python

import argparse
import codecs
import os
import sys
import re
import shutil
from pathlib import Path
from typing import Generator, List, Tuple
from pydub import AudioSegment

import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    import pygame.midi
import librosa
import soundfile
import freesound
import numpy as np
import webbrowser

DATA_ASSET_PREFIX = "data/"
KEYBOARD_ASSET_PREFIX = "keyboards/"

ANCHOR_INDICATOR = "anchor"
ANCHOR_NOTE_REGEX = re.compile(r"\s[abcdefg]$")
DESCRIPTOR_32BIT = "FLOAT"
BITS_32BIT = 32
AUDIO_ALLOWED_CHANGES_HARDWARE_DETERMINED = 0
SOUND_FADE_MILLISECONDS = 50
ALLOWED_EVENTS = {pygame.KEYDOWN, pygame.KEYUP, pygame.QUIT, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.K_ESCAPE, pygame.K_RETURN}

# GUI
pygame.init()
infoObject = pygame.display.Info()
window_width = infoObject.current_w - 100
window_height = infoObject.current_h - 100
loop = True
Playing = False

# Colors for keys and background
color_grey = (127, 127, 127)
color_white = (255, 255, 255)
color_black = (0, 0, 0)
color_red = (255, 0, 0)
color_blue = (0, 0, 255)
color_cyan = (0, 255, 255)
color_yellow = (255, 211, 67)

COLOR_INACTIVE = (159, 135, 200)
COLOR_ACTIVE = (195, 170, 237) #Slider license active color
COLOR_LIST_INACTIVE = (159, 135, 200)
COLOR_LIST_ACTIVE = (195, 170, 237)

COLOR_1 = [54, 96, 88] #Text input and square
COLOR_3 = [91, 71, 130] #Background color
COLOR_4 = [232, 206, 255] #Bars
GARNET = [159, 135, 200] #Bars circles and input inactive square

key_to_note = {
        # pygame_key_id: (pitch, black, on)
        # pygame_key_id: pygame's internal constant to represent a key
        # pitch: the pitch of this note (on the octave 0) --> not used
        # black: a boolean to know if the key is black or white
        # on: a boolean to keep track of if this note is on

        #1st octave
        pygame.K_z: (12, False, False),  # C0
        pygame.K_s: (13, True, False),  # C#/Db0
        pygame.K_x: (14, False, False),  # D0
        pygame.K_d: (15, True, False),  # D#/Eb0
        pygame.K_c: (16, False, False),  # E0
        pygame.K_v: (17, False, False),  # F0
        pygame.K_g: (18, True, False),  # F#/Gb0
        pygame.K_b: (19, False, False),  # G0
        pygame.K_h: (20, True, False),  # G#/Ab0
        pygame.K_n: (21, False, False),  # A0
        pygame.K_j: (22, True, False),  # A#/Bb0
        pygame.K_m: (23, False, False),  # B0

        #2nd octave
        pygame.K_q: (24, False, False),  # C1
        pygame.K_2: (25, True, False),  # C#/Db1
        pygame.K_w: (26, False, False),  # D1
        pygame.K_3: (27, True, False),  # D#/Eb1
        pygame.K_e: (28, False, False),  # E1
        pygame.K_r: (29, False, False),  # F1
        pygame.K_5: (30, True, False),  # F#/Gb1
        pygame.K_t: (31, False, False),  # G1
        pygame.K_6: (32, True, False),  # G#/Ab1
        pygame.K_y: (33, False, False),  # A1
        pygame.K_7: (34, True, False),  # A#/Bb1
        pygame.K_u: (35, False, False),  # B1
}

# Globals to store
Query = "Piano"
license_link = ""
License = 4
Brightness = 50
Warmth = 50
Hardness = 50
SlidersResults = [Brightness, Warmth, Hardness]
ANCHOR_NOTE = None
LOOP_SOUND = False
SUSTAINED_SOUND = False
RANGE = 10
ERROR = False


# GUI objects

class Slider:
    def __init__(self, x, y, w, h, pos,ivol):
        self.circle_x = w/100 * ivol + x
        self.volume = ivol
        self.sliderRect = pygame.Rect(x, y, w, h)
        self.selected = False;
        self.pos = pos;

    def draw(self, screen):
        pygame.draw.rect(screen, (COLOR_4), self.sliderRect)
        pygame.draw.circle(screen, (GARNET), (self.circle_x, (self.sliderRect.h / 2 + self.sliderRect.y)),
                           self.sliderRect.h * 0.5)

    def get_pos(self):
        return self.pos

    def get_volume(self):
        return self.volume

    def get_selected(self):
        return self.selected

    def select(self):
        self.selected = True

    def unselect(self):
        self.selected = False

    def set_volume(self, num):
        self.volume = num

    def update_volume(self, x):
        if x < self.sliderRect.x:
            self.volume = 1
        elif x > self.sliderRect.x + self.sliderRect.w:
            self.volume = 100
        else:
            self.volume = int((x - self.sliderRect.x) / float(self.sliderRect.w) * 100)

    def on_slider(self, x, y):
        if self.on_slider_hold(x,
                               y) or self.sliderRect.x <= x <= self.sliderRect.x + self.sliderRect.w and self.sliderRect.y <= y <= self.sliderRect.y + self.sliderRect.h:
            return True
        else:
            return False

    def on_slider_hold(self, x, y):
        if ((x - self.circle_x) * (x - self.circle_x) + (y - (self.sliderRect.y + self.sliderRect.h / 2)) * (
                y - (self.sliderRect.y + self.sliderRect.h / 2))) \
                <= (self.sliderRect.h * 1.5) * (self.sliderRect.h * 1.5):
            return True
        else:
            return False

    def handle_event(self, screen, x):
        if x < self.sliderRect.x:
            self.circle_x = self.sliderRect.x
        elif x > self.sliderRect.x + self.sliderRect.w:
            self.circle_x = self.sliderRect.x + self.sliderRect.w
        else:
            self.circle_x = x
        self.draw(screen)
        self.update_volume(x)


class OptionBox:
    def __init__(self, x, y, w, h, color, highlight_color, font, option_list, selected=0):
        self.color = color
        self.highlight_color = highlight_color
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.option_list = option_list
        self.selected = selected
        self.draw_menu = False
        self.menu_active = False
        self.active_option = -1

    def draw(self, surf):
        pygame.draw.rect(surf, self.highlight_color if self.menu_active else self.color, self.rect)
        pygame.draw.rect(surf, (0, 0, 0), self.rect, 2)
        msg = self.font.render(self.option_list[self.selected], 1, (0, 0, 0))
        surf.blit(msg, msg.get_rect(center=self.rect.center))

        if self.draw_menu:
            for i, text in enumerate(self.option_list):
                rect = self.rect.copy()
                rect.y += (i + 1) * self.rect.height
                pygame.draw.rect(surf, self.highlight_color if i == self.active_option else self.color, rect)
                msg = self.font.render(text, 1, (0, 0, 0))
                surf.blit(msg, msg.get_rect(center=rect.center))
            outer_rect = (
                self.rect.x, self.rect.y + self.rect.height, self.rect.width, self.rect.height * len(self.option_list))
            pygame.draw.rect(surf, (0, 0, 0), outer_rect, 2)

    def update(self, event_list):
        mpos = pygame.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(mpos)

        self.active_option = -1
        for i in range(len(self.option_list)):
            rect = self.rect.copy()
            rect.y += (i + 1) * self.rect.height
            if rect.collidepoint(mpos):
                self.active_option = i
                break

        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False

        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.menu_active:
                    self.draw_menu = not self.draw_menu
                elif self.draw_menu and self.active_option >= 0:
                    self.selected = self.active_option
                    self.draw_menu = False
                    return self.active_option
        return -1


class DropDown:

    def __init__(self, color_menu, color_option, x, y, w, h, font, main, options):
        self.color_menu = color_menu
        self.color_option = color_option
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.main = main
        self.options = options
        self.draw_menu = False
        self.menu_active = False
        self.active_option = -1

    def draw(self, surf):
        pygame.draw.rect(surf, self.color_menu[self.menu_active], self.rect, 0)
        msg = self.font.render(self.main, 1, (0, 0, 0))
        surf.blit(msg, msg.get_rect(center=self.rect.center))

        if self.draw_menu:
            for i, text in enumerate(self.options):
                rect = self.rect.copy()
                rect.y += (i + 1) * self.rect.height
                pygame.draw.rect(surf, self.color_option[1 if i == self.active_option else 0], rect, 0)
                msg = self.font.render(text, 1, (0, 0, 0))
                surf.blit(msg, msg.get_rect(center=rect.center))

    def update(self, event_list):
        mpos = pygame.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(mpos)

        self.active_option = -1
        for i in range(len(self.options)):
            rect = self.rect.copy()
            rect.y += (i + 1) * self.rect.height
            if rect.collidepoint(mpos):
                self.active_option = i
                break

        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False

        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.menu_active:
                    self.draw_menu = not self.draw_menu
                elif self.draw_menu and self.active_option >= 0:
                    self.draw_menu = False
                    return self.active_option
        return -1


class InputBox:

    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color =COLOR_4
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False
        self.initialTxt = text

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.text == self.initialTxt:
                self.text = ''
                self.txt_surface = FONT.render(self.text, True, self.color)
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_1 if self.active else GARNET
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)
                    # self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(600, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)

    def getText(self):
        return self.text


class button:
    def __init__(self, position, size, clr=[100, 100, 100], cngclr=None, func=None, text='', font="Raleway",
                 font_size=16, font_clr=[0, 0, 0], transparent=False):
        self.clr = clr
        self.size = size
        self.func = func
        self.surf = pygame.Surface(size)
        self.rect = self.surf.get_rect(center=position)
        self.transparent = transparent

        if cngclr:
            self.cngclr = cngclr
        else:
            self.cngclr = clr

        if len(clr) == 4:
            self.surf.set_alpha(clr[3])

        self.font = pygame.font.SysFont(font, font_size)
        self.txt = text
        self.font_clr = font_clr
        self.txt_surf = self.font.render(self.txt, 1, self.font_clr)
        self.txt_rect = self.txt_surf.get_rect(center=[wh // 2 for wh in self.size])

    def draw(self, screen):
        self.mouseover()

        self.surf.fill(self.curclr)
        self.surf.blit(self.txt_surf, self.txt_rect)
        if not self.transparent:
            screen.blit(self.surf, self.rect)

    def mouseover(self):
        self.curclr = self.clr
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            self.curclr = self.cngclr

    def call_back(self, *args):
        if self.func:
            return self.func(*args)


class text:
    def __init__(self, msg, position, clr=[232, 206, 255], font="Raleway", font_size=20, mid=False):
        self.position = position
        self.font = pygame.font.SysFont(font, font_size)
        self.txt_surf = self.font.render(msg, 1, clr)

        if len(clr) == 4:
            self.txt_surf.set_alpha(clr[3])

        if mid:
            self.position = self.txt_surf.get_rect(center=position)

    def draw(self, screen):
        screen.blit(self.txt_surf, self.position)

    def update(self, val):
        self.txt_surf = self.font.render(val, 1, COLOR_4)


# call back functions

def fn3():
    global Query, selected_license, SlidersResults, scene
    global text_info1, text_info2, text_info4, text_info5, text_info6, text_info7

    print("\n")
    print("Text query: ", Query)
    print("License option: ", selected_license)
    print("Brightness: ", SlidersResults[0])
    print("Warmth: ", SlidersResults[1])
    print("Hardness: ", SlidersResults[2])
    client = createClient()
    play_sampler(client, 3, Query, selected_license, SlidersResults[0], SlidersResults[1], SlidersResults[2])
    print("Sound name " + sound_name)
    print("Sound username " + sound_username)
    print("Sound license " + sound_license)
    print("Sound original note " + sound_note)

    text_info1 = FONT2.render("Sound name: " + sound_name, True, COLOR_4)
    text_info2 = FONT2.render("Sound username: " + sound_username, True, COLOR_4)
    text_info5 = FONT2.render("No sound matches the search. Please try again.", True, (154, 42, 42))
    text_info6 = FONT2.render(sound_note, True, color_cyan)
    text_info7 = FONT2.render(sound_license, True, (0, 0, 255))


def fn4():
    global LOOP_SOUND
    LOOP_SOUND = not LOOP_SOUND
    if LOOP_SOUND:
        button_loop.clr = COLOR_4
    else:
        button_loop.clr = GARNET

    print("LOOP_SOUND:", LOOP_SOUND)


def fn5():
    global SUSTAINED_SOUND
    SUSTAINED_SOUND = not SUSTAINED_SOUND
    if SUSTAINED_SOUND:
        button_sustained.clr = COLOR_4
    else:
        button_sustained.clr = GARNET

    print("SUSTAINED_SOUND:", SUSTAINED_SOUND)


def fn_license_link():
    global license_link

    if (not (license_link is None)) and len(license_link) > 1:
        try:
            webbrowser.open(license_link)
        except:
            print("Bad license url")
    else:
        print("No license selected yet")

# COLORS

FONT = pygame.font.SysFont('Raleway', 26, bold=False, italic=False)
FONT2 = pygame.font.SysFont('Raleway', 28, bold=False, italic=False)
TITLE = pygame.font.SysFont('Raleway', 110, bold=False, italic=False)

clock = pygame.time.Clock()
screen = pygame.display.set_mode((window_width, window_height))

text_query = FONT2.render("What kind of sound do you want?", True, (0, 0, 0))
text_sliders = FONT2.render("Select the desired values for each one of these properties", True, (0, 0, 0))
text_info = FONT2.render("Audio's data", True, (0, 0, 0))
text_info1 = FONT2.render("Sound name: ", True, COLOR_4)
text_info2 = FONT2.render("Sound username: ", True, COLOR_4)
text_info3 = FONT2.render("Sound original note: ", True, COLOR_4)
text_info4 = FONT2.render("Sound license: ", True, COLOR_4)
text_info5 = FONT2.render(" ", True, COLOR_4)
text_info6 = FONT2.render(" ", True, COLOR_4)
text_info7 = FONT2.render(" ", True, COLOR_4)

freesound_img = pygame.image.load('imgs/finallogo.png')

licenceList1 = DropDown(
    [COLOR_INACTIVE, COLOR_ACTIVE],
    [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
    1440, 204, 300, 70,
    FONT,
    "License", ["Attribution", " Attribution Noncommercial", "Creative Commons 0"])

input_box1 = InputBox(120, 530, 800, 30, "Query")

input_boxes = [input_box1]

button_loop = button(position=(1255, 240), size=(300, 70), clr=COLOR_INACTIVE, cngclr=COLOR_ACTIVE,
                     func=fn4, text='Sound loop', font_size=26)

button_sustained = button(position=(1255, 330), size=(300, 70), clr=COLOR_INACTIVE, cngclr=COLOR_ACTIVE,
                     func=fn5, text='Sustained sound', font_size=26)

button_license = button(position=(1520, 540), size=(500, 60), clr=COLOR_INACTIVE, cngclr=COLOR_ACTIVE,
                     func=fn_license_link, text='', font_size=26, transparent=True)

button1 = button(position=(850, 535), size=(200, 50), clr=COLOR_INACTIVE, cngclr=COLOR_ACTIVE, func=fn3, text='Search', font_size=26)
button_list = [button1, button_loop, button_sustained, button_license]

# Sliders
BrightnessSlider = Slider(260,  270, 500, 20, 0, SlidersResults[0]);
WarmthSlider = Slider(260, 340, 500, 20, 1, SlidersResults[1]);
HardnessSlider = Slider(260, 410, 500, 20, 2, SlidersResults[2]);
sliders = [BrightnessSlider, WarmthSlider, HardnessSlider]


# Sliders text
BrightnessTAG = text("Brightness",[120, 270], font_size=26)
WarmthTAG = text("Warmth", [120, 340], font_size=26)
HardnessTAG = text("Hardness", [120, 410], font_size=26)
SliderTAGs = [BrightnessTAG, WarmthTAG, HardnessTAG]

# Sliders Values
BrightnessValue = text("0", [800, 270], font_size=26)
WarmthValue = text("0", [800, 340], font_size=26)
HardnessValue = text("0", [800, 410], font_size=26)
SliderValues = [BrightnessValue, WarmthValue, HardnessValue];

SliderValues[0].update(str(SlidersResults[0]))
SliderValues[1].update(str(SlidersResults[1]))
SliderValues[2].update(str(SlidersResults[2]))

selected_license = 4


###############################################################

def get_audio_data(wav_path: str) -> Tuple:
    print(wav_path)
    audio_data, framerate_hz = soundfile.read(wav_path)
    array_shape = audio_data.shape
    if len(array_shape) == 1:
        channels = 1
    else:
        channels = array_shape[1]
    return audio_data, framerate_hz, channels


def get_keyboard_info(keyboard_file: str):
    with codecs.open(keyboard_file, encoding="utf-8") as k_file:
        lines = k_file.readlines()
    keys = []
    anchor_index = -1
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        match = ANCHOR_NOTE_REGEX.search(line)
        if match:
            anchor_index = i
            key = line[: match.start(0)]
        elif line.endswith(ANCHOR_INDICATOR):
            anchor_index = i
            key = line[: -len(ANCHOR_INDICATOR)]
        else:
            key = line
        keys.append(key)
    if anchor_index == -1:
        raise ValueError(
            "Invalid keyboard file."
        )
    tones = [i - anchor_index for i in range(len(keys))]
    print("Keys:", keys)
    print("Tones:", tones)
    return keys, tones


def get_or_create_key_sounds(wav_path: str, sample_rate_hz: int, channels: int, tones: List[int],clear_cache: bool, keys: List[str]) -> Generator[pygame.mixer.Sound, None, None]:
    sounds = []
    y, sr = librosa.load(wav_path, sr=sample_rate_hz, mono=channels == 1)
    file_name = os.path.splitext(os.path.basename(wav_path))[0]
    folder_containing_wav = Path(wav_path).parent.absolute()
    cache_folder_path = Path(folder_containing_wav, file_name)
    if clear_cache and cache_folder_path.exists():
        shutil.rmtree(cache_folder_path)
    if not cache_folder_path.exists():
        print("Generating samples for each key")
        os.mkdir(cache_folder_path)
    for i, tone in enumerate(tones):
        cached_path = Path(cache_folder_path, "{}.wav".format(tone))
        if Path(cached_path).exists():
            print("Loading note {} out of {} for {}".format(i + 1, len(tones), keys[i]))
            sound, sr = librosa.load(cached_path, sr=sample_rate_hz, mono=channels == 1)
        else:
            print(
                "Transposing note {} out of {} for {}".format(
                    i + 1, len(tones), keys[i]
                )
            )
            sound = librosa.effects.pitch_shift(y, sr, n_steps=tone)
            soundfile.write(cached_path, sound, sample_rate_hz, DESCRIPTOR_32BIT)
        sounds.append(sound)

    sounds = map(pygame.sndarray.make_sound, sounds)
    return sounds


def set_sampler(
        framerate_hz: int,
        channels: int):

    # audio
    pygame.mixer.quit()
    pygame.mixer.init(
        framerate_hz,
        BITS_32BIT,
        1,
        allowedchanges=AUDIO_ALLOWED_CHANGES_HARDWARE_DETERMINED,
    )
    return screen


sound_by_key = None


def play_loop(
        keys,
        key_sounds: List[pygame.mixer.Sound]
):
    global Playing
    global sound_by_key
    sound_by_key = dict(zip(keys, key_sounds))
    print("sound by key", sound_by_key)
    Playing = True


def createClient():
    api_key = os.getenv('FREESOUND_API_KEY', "xbdYSYi9lDMRwSekK8ThcIAe7gserici1pz0VoPe")
    if api_key is None:
        print("You need to set your API key as an environment variable", )
        print("named FREESOUND_API_KEY")
        sys.exit(-1)

    freesound_client = freesound.FreesoundClient()
    freesound_client.set_token(api_key)

    return freesound_client


def output(results):
    for sound in results:
        print("\t-", sound.name, "by", sound.username, sound.license,
              "\nMidi note (AC analysis): " + str(sound.ac_analysis.as_dict().get("ac_note_midi")))
        print("Note name (AC analysis): " + sound.ac_analysis.as_dict().get("ac_note_name"))

    return results[0].ac_analysis.as_dict().get("ac_note_midi")

def sound_info(results):
        global sound_name, sound_username, sound_license, sound_note, license_link
        if results is not None:
            sound_name = results[0].name
            sound_username = results[0].username
            sound_license = results[0].license
            license_link = results[0].license
            sound_note = results[0].ac_analysis.as_dict().get("ac_note_name")
        else:
            sound_name = ""
            sound_username = ""
            sound_license = ""
            sound_note = ""


def license(option):
    if str(option) == "1":
        # https://creativecommons.org/licenses/by/
        return "license:\"Attribution\" "
    elif str(option) == "2":
        # https://creativecommons.org/licenses/by-nc/
        return "license:\"Attribution Noncommercial\" "
    elif str(option) == "3":
        # https://creativecommons.org/publicdomain/zero/1.0/
        return "license:\"Creative Commons 0\" "
    elif str(option) == "4":
        return " "
    else:
        print("Invalid Option")


def brightness(b, range):
    if 1 <= int(b) <= 100:
        if (int(b) - range) < 1:
            return "ac_brightness:[1 TO " + str((int(b) + range)) + "] "
        elif (int(b) + range) > 100:
            return "ac_brightness:[" + str((int(b) - range)) + " TO 100] "
        else:
            return "ac_brightness:[" + str((int(b) - range)) + " TO " + str((int(b) + range)) + "] "
    else:
        print("Invalid Option")


def warmth(b, range):
    if 1 <= int(b) <= 100:
        if (int(b) - range) < 1:
            return "ac_warmth:[1 TO " + str((int(b) + range)) + "] "
        elif (int(b) + range) > 100:
            return "ac_warmth:[" + str((int(b) - range)) + " TO 100] "
        else:
            return "ac_warmth:[" + str((int(b) - range)) + " TO " + str((int(b) + range)) + "] "
    else:
        print("Invalid Option")


def hardness(b, range):
    if 1 <= int(b) <= 100:
        if (int(b) - range) < 1:
            return "ac_hardness:[1 TO " + str((int(b) + range)) + "] "
        elif (int(b) + range) > 100:
            return "ac_hardness:[" + str((int(b) - range)) + " TO 100] "
        else:
            return "ac_hardness:[" + str((int(b) - range)) + " TO " + str((int(b) + range)) + "] "
    else:
        print("Invalid Option")


def search(client, range, q, ql, qb, qw, qh):
    print("Search range " + str(range))

    l = license(ql)
    b = brightness(qb, range)
    w = warmth(qw, range)
    h = hardness(qh, range)

    results = client.text_search(
        query=q,
        filter="ac_single_event:true " + l + b + w + h,
        sort="score",
        fields="id,name,tags,username,license,ac_analysis,previews",
        descriptors="tonal.key_key,tonal.key_scale",
        page_size=1,
    )
    if range > 45:
        print("Out of range")
        return None
    elif results.count == 0:
        print("No sound found")
        return search(client, range + 2, q, ql, qb, qw, qh)
    else:
        return results


def freesound_search_download(client, range, q, ql, qb, qw, qh):
    results = search(client, range, q, ql, qb, qw, qh)
    sound_info(results)
    if results is not None:
        midi_note = output(results)

        path_save = os.path.normpath(
            os.getcwd() + os.sep + "data" + os.sep)  # to download all the content in the data folder

        print("Sound file extracted from Freesound:")
        results[0].retrieve_preview(path_save, results[0].name + ".mp3")

        print(results[0].name)

        file_path = os.path.normpath(path_save + os.sep + results[0].name + ".mp3")
        dst = os.path.normpath(path_save + os.sep + results[0].name + ".wav")
        audSeg = AudioSegment.from_mp3(file_path)
        if os.path.exists(dst):
            os.remove(dst)
            print("The file has been deleted successfully")
            audSeg.export(dst, format="wav")
        else:
            audSeg.export(dst, format="wav")
        return results[0].name + ".wav", midi_note
    return None, None


def remove_silence(wav_path: str):
    # read wav data
    audio, sr = librosa.load(wav_path, sr=8000, mono=True)
    print(audio.shape, sr)

    clip = librosa.effects.trim(audio, top_db=10)
    print(clip[0].shape)

    soundfile.write(wav_path, clip[0], sr)


def anchor_position(midi_note: int):
    octave = midi_note // 12 - 1
    if octave <= 3:
        return midi_note % 12
    else:
        return midi_note % 12 + 12


def set_anchor(keyboard_file: str, new_anchor: int):
    file = open(keyboard_file, "r")
    replacement = ""
    lines = file.readlines()
    # using the for loop
    for i, line in enumerate(lines):
        line = line.strip()
        new_line = line
        if not (line.endswith(" c") and i == new_anchor):
            if line.endswith(" c"):
                print("LINE PREV: ", line)
                new_line = line.replace(" c", "")
            if i == new_anchor:
                print("LINE NEW: ", line)
                new_line = line + " c"
        replacement = replacement + new_line + "\n"
    file.close()
    # opening the file in write mode
    out = open(keyboard_file, "w")
    out.write(replacement)
    out.close()



def apply_fade(audio, sr, duration=3.0):
    # convert to audio indices (samples)
    length = int(duration * sr)
    end = length
    start = 0

    out_end = audio.shape[0]
    out_start = out_end - length

    # compute fade out curve
    # linear fade
    fade_in_curve = np.linspace(0.0, 1.0, length)
    fade_out_curve = np.linspace(1.0, 0.0, length)

    # apply the curve
    audio[start:end] = audio[start:end] * fade_in_curve
    audio[out_start:out_end] = audio[out_start:out_end] * fade_out_curve


def generate_sustained_loop(sound_path: str, loop_output_path: str, extension=20):
    data, samplerate = soundfile.read(sound_path)

    trimed_data = []
    loopable_data = []
    test_data = []

    # IDENTIFY THE START FRAME AND ENDFRAME
    atack_length = 0.6
    tail_lenght = 0.8

    #CALCULATE NUMBER OF FRAMES ADDED

    t = (len(data) / float(samplerate)) * (tail_lenght - atack_length)
    repetitions = int(extension/t)
    duration = (len(data) / float(samplerate))
    print("duration:" + str(duration))

    # SEPARETE THE TRACK IN TWO: ATACK SECTION, LOOP SECTION
    for i in range(0, int(len(data) * tail_lenght)):
        trimed_data.append(data[i])

    for i in range(int(len(data) * atack_length), int(len(data) * tail_lenght)):
        loopable_data.append(data[i])

    soundfile.write(loop_output_path.split('.')[0] + "_TEMP_TRIMMED.wav", trimed_data, samplerate)
    soundfile.write(loop_output_path.split('.')[0] + "_TEMP_LOOP.wav", loopable_data, samplerate)

    # CORRECT LOOP SECTION
    orig, sr = soundfile.read(loop_output_path.split('.')[0] + "_TEMP_LOOP.wav")
    out = orig.copy()
    apply_fade(out, sr, duration=(librosa.get_duration(y=orig, sr=sr) * 0.5))
    soundfile.write(loop_output_path.split('.')[0] + "_TEMP_LOOP.wav", out, sr)

    # JOIN THE ATACK SECTION AND LOOP SECTION
    tdata, tsamplerate = soundfile.read(loop_output_path.split('.')[0] + "_TEMP_TRIMMED.wav")
    ldata, lsamplerate = soundfile.read(loop_output_path.split('.')[0] + "_TEMP_LOOP.wav")

    tdata = tdata.tolist()

    l = len(tdata)
    dl = l - int((len(ldata) * 0.5))

    for j in range(repetitions):
        for i in range(len(ldata)):
            tdata.append(ldata[i])

    for j in range(repetitions):
        for i in range(len(ldata)):
            tdata[dl + (j * len(ldata)) + i] += ldata[i]

    soundfile.write(loop_output_path, tdata, samplerate)

    duration = (len(tdata) / float(samplerate))
    print("duration:" + str(duration))

    # DELETE TEMPORAL FILES
    os.remove(loop_output_path.split('.')[0] + "_TEMP_TRIMMED.wav")
    os.remove(loop_output_path.split('.')[0] + "_TEMP_LOOP.wav")

    return loop_output_path


def draw_keyboard(window) -> None:
    '''Draw the octave keyboard on screen'''

    window_w = 600 #window.get_width()
    window_h = 350 #window.get_height()

    margin = window_w // 140

    white_width = (window_w - 8 * margin) // 7
    black_width = white_width // 2 + 2 * margin

    left = margin
    top = margin
    bottom = window_h - top

    # Draw white keys
    for key in key_to_note:
        note, black, on = key_to_note[key]
        if black:
            continue
        if note != ANCHOR_NOTE:
            pygame.draw.rect(window, color_red if on else color_white, (left + window_width / 6, top + window_height / 1.6, white_width, bottom - top))
        else:
            pygame.draw.rect(window, color_red if on else color_cyan, (left + window_width / 6, top + window_height / 1.6, white_width, bottom - top))
        left += margin + white_width

    # Reset left for black keys
    left = margin + white_width + margin // 2 - black_width // 2

    bottom = bottom - (bottom - top) // 3

    # Draw black keys
    for key in key_to_note:
        note, black, on = key_to_note[key]
        if not black:
            continue
        if note == 18 or note == 25 or note == 30:  # Skip the inexistant black keys
            left += margin + white_width
        if note != ANCHOR_NOTE:
            pygame.draw.rect(window, color_blue if on else color_black, (left + window_width / 6, top + window_height / 1.6, black_width, bottom - top))
        else:
            pygame.draw.rect(window, color_blue if on else color_cyan, (left + window_width / 6, top + window_height / 1.6, black_width, bottom - top))
        left += margin + white_width


def play_sampler(client, range, q, ql, qb, qw, qh):
    global ANCHOR_NOTE, ERROR

    wav_name, midi_note = freesound_search_download(client, range, q, ql, qb, qw, qh)

    if wav_name is not None:
        wav_path = os.path.normpath(os.getcwd() + os.sep + "data" + os.sep + wav_name)
        keyboard_path = os.path.normpath(os.getcwd() + os.sep + "keyboards" + os.sep + "piano.txt")
        clear_cache = False
        keyboard_anchor = anchor_position(midi_note)
        ANCHOR_NOTE = keyboard_anchor + 12;
        set_anchor(keyboard_path, keyboard_anchor)

        remove_silence(wav_path)

        if SUSTAINED_SOUND:
            wav_path = generate_sustained_loop(wav_path, wav_path.split('.')[0] + "_l.wav", extension=20)

        audio_data, framerate_hz, channels = get_audio_data(wav_path)
        results = get_keyboard_info(keyboard_path)
        keys, tones = results
        key_sounds = get_or_create_key_sounds(
            wav_path, framerate_hz, channels, tones, clear_cache, keys
        )
        screen = set_sampler(framerate_hz, channels)
        play_loop(keys, key_sounds)
        ERROR = False
    else:
        ERROR = True


# Main Loop
if __name__ == "__main__":

    while loop:
        #print(pygame.mouse.get_pos())
        screen.fill(COLOR_3)
        pygame.display.set_caption('Freesound sampler')

        slider_rect = pygame.rect.Rect(100, 200, 900, 260)
        input_rect = pygame.rect.Rect(100, 480, 900, 100)
        info_rect = pygame.rect.Rect(1090, 385, 670, 200)
        pygame.draw.rect(screen, (124, 102, 164), slider_rect, border_radius=20)
        pygame.draw.rect(screen, (124, 102, 164), input_rect, border_radius=20)
        pygame.draw.rect(screen, (124, 102, 164), info_rect, border_radius=20)
        draw_keyboard(screen)

        screen.blit(text_info, dest=(1120, 400))
        screen.blit(text_info1, dest=(1120, 430))
        screen.blit(text_info2, dest=(1120, 460))
        screen.blit(text_info3, dest=(1120, 490))
        screen.blit(text_info4, dest=(1120, 520))
        screen.blit(text_info6, dest=(1313, 490))
        screen.blit(text_info7, dest=(1265, 520))

        if ERROR:
            screen.blit(text_info5, dest=(1120, 550))

        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    fn3()
                if event.key == pygame.K_ESCAPE:
                    loop = False
                    break
            if event.type == pygame.QUIT:
                loop = False
                break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for s in sliders:
                    if s.on_slider_hold(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]):
                        s.select()
                if event.button == 1:
                    pos = pygame.mouse.get_pos()
                    for b in button_list:
                        if b.rect.collidepoint(pos):
                            b.call_back()
            for s in sliders:
                if s.get_selected():
                    s.handle_event(screen, pygame.mouse.get_pos()[0])
                    SlidersResults[s.get_pos()] = s.get_volume()
                    SliderValues[s.get_pos()].update(str(s.get_volume()))
            if event.type == pygame.MOUSEBUTTONUP:
                for s in sliders:
                    s.unselect()
            for box in input_boxes:
                box.handle_event(event)
                Query = box.getText()
            if event.type == pygame.QUIT:
                done = True
            if Playing:
                if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                    key = event.unicode
                    if key is None:
                        continue
                    try:
                        sound = sound_by_key[key]
                    except KeyError:
                        continue
                    print("sound:", sound)
                    if event.type == pygame.KEYDOWN:
                        event_key = event.key
                        if not ERROR:
                            if event_key in key_to_note:
                                note, black, on = key_to_note[event_key]
                                if not on:
                                    key_to_note[event_key] = note, black, True
                            sound.stop()
                            if LOOP_SOUND:
                                sound.play(fade_ms=SOUND_FADE_MILLISECONDS, loops=-1)
                            else:
                                sound.play(fade_ms=SOUND_FADE_MILLISECONDS)
                    elif event.type == pygame.KEYUP:
                        event_key = event.key
                        if not ERROR:
                            if event_key in key_to_note:
                                note, black, on = key_to_note[event_key]
                                if on:
                                    key_to_note[event_key] = note, black, False
                            sound.fadeout(SOUND_FADE_MILLISECONDS)

        License = licenceList1.update(event_list)

        if License >= 0:
            licenceList1.main = licenceList1.options[License]
            selected_license = License + 1
            print(selected_license)

        for box in input_boxes:
            box.update()

        for box in input_boxes:
            box.draw(screen)
        for b in button_list:
            b.draw(screen)
        for s in sliders:
            s.draw(screen)
        licenceList1.draw(screen)
        for t in SliderTAGs:
            t.draw(screen)
        for v in SliderValues:
            v.draw(screen)

        screen.blit(freesound_img, dest=(380, 10))
        screen.blit(text_query, dest=(120, 500))
        screen.blit(text_sliders, dest=(120, 220))

        draw_keyboard(screen)
        pygame.display.update()
        pygame.display.flip()
        clock.tick(30)