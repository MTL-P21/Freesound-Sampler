import freesound

client = freesound.FreesoundClient()
client.set_token("xbdYSYi9lDMRwSekK8ThcIAe7gserici1pz0VoPe","token")

results = client.text_search(query="trumpet",fields="id,name,previews")

for sound in results:
    sound.retrieve_preview("/tests/",sound.name+".mp3")
    print(sound.name)