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

import librosa
import pygame
import soundfile
import freesound

DATA_ASSET_PREFIX = "data/"
KEYBOARD_ASSET_PREFIX = "keyboards/"

ANCHOR_INDICATOR = "anchor"
ANCHOR_NOTE_REGEX = re.compile(r"\s[abcdefg]$")
DESCRIPTOR_32BIT = "FLOAT"
BITS_32BIT = 32
AUDIO_ALLOWED_CHANGES_HARDWARE_DETERMINED = 0
SOUND_FADE_MILLISECONDS = 50
ALLOWED_EVENTS = {pygame.KEYDOWN, pygame.KEYUP, pygame.QUIT}
LOOP_SOUND = False;
RANGE = 10

# gui part

window_width = 1280
window_height =720
scene = 0

# Globals to store
Query = "Piano"
selected_license = "Attribution"
License = "Attribution"
Brightness = 0
Warmth = 0
Hardness = 0
SlidersResults = [Brightness, Warmth, Hardness]


class Slider:
    def __init__(self, x, y, w, h, pos):
        self.circle_x = x
        self.volume = 0
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
            self.volume = 0
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
        # print(self.volume)


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


class DropDown():

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
                 font_size=16, font_clr=[0, 0, 0]):
        self.clr = clr
        self.size = size
        self.func = func
        self.surf = pygame.Surface(size)
        self.rect = self.surf.get_rect(center=position)

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
        self.txt_surf = self.font.render(val, 1, [100, 100, 100])


# call back functions


def fn3():
    global Query
    global selected_license
    global SlidersResults
    global scene

    print("\n")
    print("Text query: ", Query, "\n")
    print("License option: ", selected_license, "\n")
    print("Brightness: ", SlidersResults[0], "\n")
    print("Warmth: ", SlidersResults[1], "\n")
    print("Hardness: ", SlidersResults[2], "\n")
    scene = -1
    client = createClient()
    play_sampler(client, 2, Query, 4, SlidersResults[0], SlidersResults[1], SlidersResults[2])


def fn4():
    global LOOP_SOUND
    #button_loop.txt = "SOUND LOOP = " + str(LOOP_SOUND)
    LOOP_SOUND = not LOOP_SOUND
    if LOOP_SOUND:
        button_loop.clr = COLOR_4
    else:
        button_loop.clr = GARNET

    print("LOOP_SOUND:", LOOP_SOUND)



pygame.init()
COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')
#FONT = pygame.font.Font(None, 32)
FONT = pygame.font.SysFont('Raleway', 26, bold=False, italic=False)
FONT2 = pygame.font.SysFont('Raleway', 28, bold=False, italic=False)
TITLE = pygame.font.SysFont('Raleway', 110, bold=False, italic=False)
#font2 = pygame.font.Font(None, 100)
#font2 = pygame.font.SysFont('Raleway', 72, bold=False, italic=False)

clock = pygame.time.Clock()
screen = pygame.display.set_mode((window_width, window_height))

text_surface = TITLE.render("sampler", True, (0, 0, 0))
text_query = FONT2.render("What kind of sound do you want?", True, (0, 0, 0))
text_sliders = FONT2.render("Select values for each one of this properties:", True, (0, 0, 0))
freesound_img = pygame.image.load('../freesound.png')

# COLORS
COLOR_INACTIVE = (159, 135, 200)
COLOR_ACTIVE = (195, 170, 237) #Slider license active color
COLOR_LIST_INACTIVE = (159, 135, 200)
COLOR_LIST_ACTIVE = (195, 170, 237)

COLOR_1 = [54, 96, 88] #Text input and square
COLOR_2 = [159, 135, 200] #Slider button inactive
COLOR_3 = [91, 71, 130] #Background color
COLOR_4 = [232, 206, 255] #Bars
COLOR_5 = [241, 176, 143] #Not used
GARNET = [159, 135, 200] #Bars circles and input inactive square

list1 = DropDown(
    [COLOR_INACTIVE, COLOR_ACTIVE],
    [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
    (window_width / 2) - 100, window_height / 3, 190, 50,
    FONT,
    "Chnnels", ["Single Channel", "Dual Channel"])

typeList1 = DropDown(
    [COLOR_INACTIVE, COLOR_ACTIVE],
    [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
    (window_width / 2) - 300, window_height / 3, 190, 50,
    FONT,
    "Format", ["wav", "aiff", "ogg", "mp3", "m4a", "flac"])

licenceList1 = DropDown(
    [COLOR_INACTIVE, COLOR_ACTIVE],
    [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
    window_width/2 + 150, window_height/4 + 30, 300, 70,
    FONT,
    "License", ["Attribution ", " Attribution Noncommercial", "Creative Commons 0"])

input_box1 = InputBox(window_width/4 - 190, window_height/2 + 127, window_width * 2 , 30, "Query")
#input_box2 = InputBox(100, 300, 140, 32, "Tags")

input_boxes = [input_box1]

button_loop = button(position=(window_width/2 + 300, window_height/2 - 10), size=(300, 70), clr=COLOR_INACTIVE, cngclr=COLOR_ACTIVE,
                     func=fn4, text='Sound loop', font_size=26)

button1 = button(position=(950, 670), size=(300, 70), clr=COLOR_INACTIVE, cngclr=COLOR_ACTIVE, func=fn3, text='G o !', font_size=30)
button_list = [button1, button_loop]

#text1 = text(msg=str(LOOP_SOUND), position=(300, 325), clr=[100, 100, 100], font="Segoe Print", font_size=15)
#text_list = [text1]

# Sliders
BrightnessSlider = Slider(window_width/4 - 30,  window_height/4 + 70, 300, 20, 0);
WarmthSlider = Slider(window_width/4 - 30, window_height/4 + 130, 300, 20, 1);
HardnessSlider = Slider(window_width/4 - 30, window_height/4 + 190, 300, 20, 2);
sliders = [BrightnessSlider, WarmthSlider, HardnessSlider]
# Sliders text
BrightnessTAG = text("Brightness", [window_width/4 - 190, window_height/4 + 70], font_size=26)
WarmthTAG = text("Warmth", [window_width/4 - 190, window_height/4 + 130], font_size=26)
HardnessTAG = text("Hardness", [window_width/4 - 190, window_height/4 + 190], font_size=26)
SliderTAGs = [BrightnessTAG, WarmthTAG, HardnessTAG]
# Sliders Values
BrightnessValue = text("0", [window_width/2, window_height/4 + 70], font_size=26)
WarmthValue = text("0", [window_width/2, window_height/4 + 130], font_size=26)
HardnessValue = text("0", [window_width/2, window_height/4 + 190], font_size=26)
SliderValues = [BrightnessValue, WarmthValue, HardnessValue];

selected_license = ""


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


def get_or_create_key_sounds(
        wav_path: str,
        sample_rate_hz: int,
        channels: int,
        tones: List[int],
        clear_cache: bool,
        keys: List[str],
) -> Generator[pygame.mixer.Sound, None, None]:
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
    pygame.quit()
    pygame.display.init()
    pygame.display.set_caption("sampler")

    # block events that we don't want, this must be after display.init
    pygame.event.set_blocked(None)
    pygame.event.set_allowed(list(ALLOWED_EVENTS))

    # audio
    pygame.mixer.init(
        framerate_hz,
        BITS_32BIT,
        channels,
        allowedchanges=AUDIO_ALLOWED_CHANGES_HARDWARE_DETERMINED,
    )
    screen = pygame.display.set_mode((window_width, window_height))
    screen.fill(COLOR_3)
    pygame.display.update()
    return screen


def play_loop(
        keys,
        key_sounds: List[pygame.mixer.Sound]
):
    sound_by_key = dict(zip(keys, key_sounds))
    print("sound by key", sound_by_key)

    loop = True
    while loop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                loop = False
                break

            elif event.key == pygame.K_ESCAPE:
                loop = False
                break

            # print("event:", event.unicode)
            key = event.unicode
            # print("key:", key)

            if key is None:
                continue
            try:
                sound = sound_by_key[key]
            except KeyError:
                continue
            print("sound:", sound)
            if event.type == pygame.KEYDOWN:
                sound.stop()
                if LOOP_SOUND:
                    sound.play(fade_ms=SOUND_FADE_MILLISECONDS, loops=-1)
                else:
                    sound.play(fade_ms=SOUND_FADE_MILLISECONDS)
            elif event.type == pygame.KEYUP:
                sound.fadeout(SOUND_FADE_MILLISECONDS)

    pygame.quit()


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

    if results.count == 0:
        print("No sound found")
        return search(client, range + 1, q, ql, qb, qw, qh)
    else:
        return results


def freesound_search_download(client, range, q, ql, qb, qw, qh):
    results = search(client, range, q, ql, qb, qw, qh)
    midi_note = output(results)

    path_save = os.path.normpath(
        os.getcwd() + os.sep + "data" + os.sep)  # to download all the content in the data folder

    print("Sound file extracted from Freesound:")
    results[0].retrieve_preview(path_save, results[0].name + ".mp3")

    print(results[0].name)
    """
    print("Sound files extracted from Freesound:")
    for sound in results:
        sound.retrieve(path_save, sound.name)
        print(sound.name)
    """
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


def remove_silence(wav_path: str):
    # read wav data
    audio, sr = librosa.load(wav_path, sr=8000, mono=True)
    print(audio.shape, sr)

    clip = librosa.effects.trim(audio, top_db=10)
    print(clip[0].shape)

    soundfile.write(wav_path, clip[0], sr)


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


def play_sampler(client, range, q, ql, qb, qw, qh):
    wav_name, midi_note = freesound_search_download(client, range, q, ql, qb, qw, qh)

    wav_path = os.path.normpath(os.getcwd() + os.sep + "data" + os.sep + wav_name)
    keyboard_path = os.path.normpath(os.getcwd() + os.sep + "keyboards" + os.sep + "qwerty_piano.txt")
    clear_cache = False

    set_anchor(keyboard_path, midi_note - 37)

    remove_silence(wav_path)
    audio_data, framerate_hz, channels = get_audio_data(wav_path)
    results = get_keyboard_info(keyboard_path)
    keys, tones = results
    key_sounds = get_or_create_key_sounds(
        wav_path, framerate_hz, channels, tones, clear_cache, keys
    )
    screen = set_sampler(framerate_hz, channels)
    play_loop(keys, key_sounds)


# Main Loop
while scene == 0:
    #print(pygame.mouse.get_pos())
    screen.fill(COLOR_3)
    pygame.display.set_caption('Query and tags')

    slider_rect = pygame.rect.Rect(window_width/4 - 230, window_height/4 - 4, 2 / 4 * window_width,
                                 window_height/3 + 10)
    input_rect = pygame.rect.Rect(window_width / 4 - 230, window_height / 2 + 80, window_width/2 + 80,
                                   window_height / 4 - 80)
    pygame.draw.rect(screen, (124, 102, 164), slider_rect, border_radius=20)
    pygame.draw.rect(screen, (124, 102, 164), input_rect, border_radius=20)

    event_list = pygame.event.get()
    for event in event_list:
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
    License = licenceList1.update(event_list)

    if License >= 0:
        licenceList1.main = licenceList1.options[License]
        selected_license = licenceList1.main



    for box in input_boxes:
        box.update()

    for box in input_boxes:
        box.draw(screen)
    for b in button_list:
        b.draw(screen)
    #for t in text_list:
        #t.draw(screen)
    for s in sliders:
        s.draw(screen)
    licenceList1.draw(screen)
    for t in SliderTAGs:
        t.draw(screen)
    for v in SliderValues:
        v.draw(screen)

    screen.blit(freesound_img, (window_width/4 - 200 , window_height/4 - 190))
    screen.blit(text_surface, dest=(window_width/4 + 360, window_height/4 - 125))
    screen.blit(text_query, dest=(window_width/4 - 190, window_height/4 + 275))
    screen.blit(text_sliders, dest=(window_width/4 - 190, window_height/4 + 20))



    pygame.display.update()
    pygame.display.flip()
    clock.tick(30)
