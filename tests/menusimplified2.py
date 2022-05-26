from __future__ import print_function
import freesound
import os
import sys


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


def search(range):
    client = createClient()
    print("Search range " + str(range))

    q = "drum"

    l = license(4)
    b = brightness(23, range)
    w = warmth(45, range)
    h = hardness(76, range)

    # print("FILTERS: ac_single_event:true " + l + b + w + h)

    results = client.text_search(
        query=q,
        filter="ac_single_event:true " + l + b + w + h,
        sort="score",
        fields="id,name,tags,username,license,analysis,ac_analysis",
        descriptors="tonal.key_key,tonal.key_scale",
        page_size=1,
    )

    printpage1(results)

    if results.count == 0:
        print("No sound found")
        search(range+1)


search(2)
