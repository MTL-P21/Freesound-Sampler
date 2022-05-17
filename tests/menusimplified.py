from __future__ import print_function
import freesound
import os
import sys


def createClient():
    api_key = os.getenv('FREESOUND_API_KEY', "xbdYSYi9lDMRwSekK8ThcIAe7gserici1pz0VoPe")
    if api_key is None:
        print("You need to set your API key as an evironment variable", )
        print("named FREESOUND_API_KEY")
        sys.exit(-1)

    freesound_client = freesound.FreesoundClient()
    freesound_client.set_token(api_key)

    return freesound_client


def printpage1(results):
    for sound in results:
        print("\t-", sound.name, "by", sound.username, sound.license)
        print(str(sound.tags))


def license():
    number = input(
        "Select the license of the sound you want to download\n1-Attribution\n2-Attribution Noncommercial\n3-Creative Commons 0\n ->")
    if number == "1":
        return "license:Attribution "
    elif number == "2":
        return "license:Attribution Noncommercial "
    elif number == "3":
        return "license:Creative Commons 0 "  # revisar
    else:
        print("Invalid Option")
        license()


def channels():
    channel = input("Select the number of channels of the sound you want to download: ")
    if channel == "1":
        return "channels:1 "
    elif channel == "2":
        return "channels:2 "
    else:
        print("Invalid Option")
        channels()


def sharpness():
    s = input("From 1 to 100 select the desired sharpness for the sound: ")
    if 1 <= int(s) <= 100:
        return "ac_sharpness:[" + str((int(s) - 10)) + " TO " + str((int(s) + 10)) + "] "
    else:
        print("Invalid Option")
        sharpness()


def brightness():
    b = input("From 1 to 100 select the desired brightness for the sound: ")
    if 1 <= int(b) <= 100:
        return "ac_brightness:[" + str((int(b) - 10)) + " TO " + str((int(b) + 10)) + "] "
    else:
        print("Invalid Option")
        brightness()


def depth():
    d = input("From 1 to 100 select the desired depth for the sound: ")
    if 1 <= int(d) <= 1000:
        return "ac_depth:[" + str((int(d) - 10)) + " TO " + str((int(d) + 10)) + "] "
    else:
        print("Invalid Option")
        depth()


notes = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]


def note():
    n = input("Input the desired note [“A”, “A#”, “B”, “C”, “C#”, “D”, “D#”, “E”, “F”, “F#”, “G”, “G#”]: ")
    if n in notes:
        return "ac_note_name:" + n + " "
    else:
        print("Invalid Option")
        note()


def search():
    client = createClient()

    q = input("Which sound do you wish to download: ")

    l = license()
    c = channels()
    s = sharpness()
    b = brightness()
    d = depth()
    n = note()

    print("FILTERS: ac_single_event:true " + l + c + s + b + d)

    results = client.text_search(
        query=q,  # "drum",
        filter="ac_single_event:true " + l + c + s + b + d,  # ac_single_event:true
        sort="score"
    )
    printpage1(results)


search()
