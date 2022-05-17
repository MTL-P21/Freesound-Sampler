import os
from pydub import AudioSegment

print("Name of the file you want to convert from mp3 to wav:")
file_name = input()

audio_file = os.path.normpath(os.getcwd() + os.sep + os.pardir + os.sep + "data" + os.sep + file_name + ".mp3")
path_save = os.path.normpath(os.getcwd() + os.sep + os.pardir + os.sep + "data" + os.sep + file_name + ".wav")

audSeg = AudioSegment.from_mp3(audio_file)
if os.path.exists(path_save):
    os.remove(path_save)
    print("The file has been deleted successfully")
    audSeg.export(path_save, format="wav")
else:
    audSeg.export(path_save, format="wav")