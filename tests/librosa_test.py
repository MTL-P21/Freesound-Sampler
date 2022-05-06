import librosa
import soundfile as sf
import os

filename = os.path.normpath(os.getcwd() + os.sep + os.pardir + os.sep + "data" + os.sep + "TrumpetValves_1.wav.mp3")

y, sr = librosa.load(filename)

y_third = librosa.effects.pitch_shift(y, sr=sr, n_steps=4)

y_tritone = librosa.effects.pitch_shift(y, sr=sr, n_steps=-6)

sf.write('TrumpetValves_1_Shift_up.mp3', y_third, sr, subtype='PCM_24')
sf.write('TrumpetValves_1_Shift_down.mp3', y_tritone, sr, subtype='PCM_24')