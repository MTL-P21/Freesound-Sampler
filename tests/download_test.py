import os

import freesound

client = freesound.FreesoundClient()
client.set_token("xbdYSYi9lDMRwSekK8ThcIAe7gserici1pz0VoPe","token")

results = client.text_search(query="trumpet",fields="id,name,previews")

for sound in results:
    path_save = os.path.normpath(os.getcwd() + os.sep + os.pardir + "/data/") #to download all the content in the data folder
    sound.retrieve_preview(path_save,sound.name+".mp3")
    print(sound.name)