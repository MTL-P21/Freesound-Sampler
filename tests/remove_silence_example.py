import os
import librosa
import soundfile as sf

audio_file = os.path.normpath(os.getcwd() + os.sep + os.pardir + os.sep + "data" + os.sep + "ELECTRIC PIANO (C3).wav")
path_save = os.path.normpath(os.getcwd() + os.sep + os.pardir + os.sep + "data" + os.sep + "ELECTRIC PIANO (C3)_SILENCE_REMOVED.wav")

#read wav data
audio, sr = librosa.load(audio_file, sr= 8000, mono=True)
print(audio.shape, sr)

clip = librosa.effects.trim(audio, top_db= 10)
print(clip[0].shape)

sf.write(path_save, clip[0], sr)