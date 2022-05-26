from __future__ import print_function
import freesound
import os
import sys

RANGE = 10


def createClient():
    api_key = os.getenv('FREESOUND_API_KEY', "xbdYSYi9lDMRwSekK8ThcIAe7gserici1pz0VoPe")
    if api_key is None:
        print("You need to set your API key as an environment variable", )
        print("named FREESOUND_API_KEY")
        sys.exit(-1)

    freesound_client = freesound.FreesoundClient()
    freesound_client.set_token(api_key)

    return freesound_client


def printpage1(results):
    for sound in results:
        print("\t-", sound.name, "by", sound.username, sound.license,
              "\nMidi note (AC analysis): " + str(sound.ac_analysis.as_dict().get("ac_note_midi")))
        print("Note name (AC analysis): " + sound.ac_analysis.as_dict().get("ac_note_name"))


def license():
    option = input(
        "Select the license of the sound you want to download\n1-Attribution\n2-Attribution Noncommercial\n3-Creative Commons 0\n4-All\n")
    if option == "1":
        # https://creativecommons.org/licenses/by/
        return "license:\"Attribution\" "
    elif option == "2":
        # https://creativecommons.org/licenses/by-nc/
        return "license:\"Attribution Noncommercial\" "
    elif option == "3":
        # https://creativecommons.org/publicdomain/zero/1.0/
        return "license:\"Creative Commons 0\" "
    elif option == "4":
        return " "
    else:
        print("Invalid Option")
        return license()


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


def search():
    client = createClient()

    q = input("Which sound do you wish to download?  ")

    l = license()
    c = channels()
    b = brightness()
    w = warmth()
    h = hardness()

    #print("FILTERS: ac_single_event:true " + l + c + b + w + h)

    results = client.text_search(
        query=q,
        filter="ac_single_event:true " + l + c + b + w + h,
        sort="score",
        fields="id,name,tags,username,license,analysis,ac_analysis",
        descriptors="tonal.key_key,tonal.key_scale",
        page_size=50,
    )

    printpage1(results)

    if results.count == 0:
        print("No sound found")


search()


# unused functions
def sharpness():
    s = input("From 1 to 100 select the desired sharpness for the sound: ")
    if 1 <= int(s) <= 100:
        return "ac_sharpness:[" + str((int(s) - 10)) + " TO " + str((int(s) + 10)) + "] "
    else:
        print("Invalid Option")
        sharpness()


notes = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]


# Freesound no te devuelve nada
def note():
    n = input("Input the desired note [“A”, “A#”, “B”, “C”, “C#”, “D”, “D#”, “E”, “F”, “F#”, “G”, “G#”]: ")
    if n in notes:
        return "ac_note_name:" + n + " "
    else:
        print("Invalid Option")
        note()


def depth():
    d = input("From 1 to 100 select the desired depth for the sound: ")
    if 1 <= int(d) <= 1000:
        return "ac_depth:[" + str((int(d) - 10)) + " TO " + str((int(d) + 10)) + "] "
    else:
        print("Invalid Option")
        depth()


'''
        print("Tonality (ac_analysis): " + sound.ac_analysis.as_dict().get("ac_tonality"))
        print("Key & Scale (analysis): " + sound.analysis.as_dict().get("tonal").get("key_key") + " " + sound.analysis.as_dict().get("tonal").get("key_scale"))

        for key, value in sound.analysis.as_dict().items():
            print(key, ' : ', value)
        for key, value in sound.ac_analysis.as_dict().items():
            print(key, ' : ', value)
'''
