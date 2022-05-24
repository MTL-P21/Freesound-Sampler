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

RANGE = 10

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

    screen_width = 500
    screen_height = 300
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.update()
    return screen


def play_loop(
    keys,
    key_sounds: List[pygame.mixer.Sound],
):
    sound_by_key = dict(zip(keys, key_sounds))
    print("sound by key",sound_by_key)

    loop = True
    while loop:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                loop = False
                break
            elif event.key == pygame.K_ESCAPE:
                loop = False
                break

            #print("event:", event.unicode)
            key = event.unicode
            #print("key:", key)

            if key is None:
                continue
            try:
                sound = sound_by_key[key]
            except KeyError:
                continue
            print("sound:", sound)
            if event.type == pygame.KEYDOWN:
                sound.stop()
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


def license():
    option = input(
        "Select the license of the sound you want to download\n1-Attribution\n2-Attribution Noncommercial\n3-Creative Commons 0\n ->")
    if option == "1":
        # https://creativecommons.org/licenses/by-nc/4.0/
        return "license:\"Attribution\" "
    elif option == "2":
        # https://creativecommons.org/licenses/by-nc/3.0/
        return "license:\"Attribution Noncommercial\" "
    elif option == "3":
        # https://creativecommons.org/publicdomain/zero/1.0/
        return "license:\"Creative Commons 0\" "
    else:
        print("Invalid Option")
        return license()


def output(results):
    for sound in results:
        print("\t-", sound.name, "by", sound.username, sound.license,
              "Midi note (AC analysis): " + str(sound.ac_analysis.as_dict().get("ac_note_midi")))
        print("Note name (ac_analysis): " + sound.ac_analysis.as_dict().get("ac_note_name"))

    return results[0].ac_analysis.as_dict().get("ac_note_midi")


def channels():
    channel = input("Select the number of channels of the sound you want to download: ")
    if channel == "1":
        return "channels:1 "
    elif channel == "2":
        return "channels:2 "
    else:
        print("Invalid Option")
        return channels()


def brightness():
    b = input("From 1 to 100 select the desired brightness for the sound: ")
    if 1 <= int(b) <= 100:
        if (int(b) - RANGE) < 1:
            return "ac_brightness:[1 TO " + str((int(b) + RANGE)) + "] "
        elif (int(b) + RANGE) > 100:
            return "ac_brightness:[" + str((int(b) - RANGE)) + " TO 100] "
        else:
            return "ac_brightness:[" + str((int(b) - RANGE)) + " TO " + str((int(b) + RANGE)) + "] "
    else:
        print("Invalid Option")
        return brightness()


def warmth():
    b = input("From 1 to 100 select the desired warmth for the sound: ")
    if 1 <= int(b) <= 100:
        if (int(b) - RANGE) < 1:
            return "ac_warmth:[1 TO " + str((int(b) + RANGE)) + "] "
        elif (int(b) + RANGE) > 100:
            return "ac_warmth:[" + str((int(b) - RANGE)) + " TO 100] "
        else:
            return "ac_warmth:[" + str((int(b) - RANGE)) + " TO " + str((int(b) + RANGE)) + "] "
    else:
        print("Invalid Option")
        return warmth()


def hardness():
    b = input("From 1 to 100 select the desired hardness for the sound: ")
    if 1 <= int(b) <= 100:
        if (int(b) - RANGE) < 1:
            return "ac_hardness:[1 TO " + str((int(b) + RANGE)) + "] "
        elif (int(b) + RANGE) > 100:
            return "ac_hardness:[" + str((int(b) - RANGE)) + " TO 100] "
        else:
            return "ac_hardness:[" + str((int(b) - RANGE)) + " TO " + str((int(b) + RANGE)) + "] "
    else:
        print("Invalid Option")
        return hardness()


def search(client):


    q = input("Which sound do you wish to download?  ")
    l = license()
    #c = channels()
    b = brightness()
    w = warmth()
    h = hardness()

    results = client.text_search(
        query=q,
        filter="ac_single_event:true channels:1 " + l + b + w + h,
        sort="score",
        fields="id,name,tags,username,license,ac_analysis,previews",
        page_size=1,
    )

    if results.count == 0:
        print("No sound found")
        return search(client)
    else:
        return results



def freesound_search_download():
    client = createClient()
    results = search(client)
    midi_note = output(results)

    path_save = os.path.normpath(os.getcwd() + os.sep + "data" + os.sep)  # to download all the content in the data folder

    print("Sound file extracted from Freesound:")
    results[0].retrieve_preview(path_save, results[0].name+".mp3")

    print(results[0].name)
    """
    print("Sound files extracted from Freesound:")
    for sound in results:
        sound.retrieve(path_save, sound.name)
        print(sound.name)
    """
    file_path = os.path.normpath(path_save + os.sep + results[0].name+".mp3")
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


def play_sampler():
    wav_name, midi_note = freesound_search_download()

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
    set_sampler(framerate_hz, channels)
    play_loop(keys, key_sounds)


if __name__ == "__main__":
    play_sampler()