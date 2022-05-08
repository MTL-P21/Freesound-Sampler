import os
import librosa
import soundfile as sf


y, sr = librosa.load( ".."+ os.sep+"data" + os.sep + "bowl.wav",duration=5.0)
y_shifted = librosa.effects.pitch_shift(y,sr, n_steps=4) # shifted by 4 half steps
sf.write(".."+ os.sep+ "data" + os.sep + "bowl_shifted.wav", y_shifted, 48000, 'PCM_24')