# We'll need numpy for some mathematical operations
import numpy as np

# matplotlib for displaying the output
import matplotlib.pyplot as plt
import matplotlib.style as ms
ms.use('seaborn-muted')

# Librosa for audio
import librosa
# And the display module for visualization
import librosa.display

filename = './wav/01 - An Angel Came Down.wav'
y, sr = librosa.load(filename)
duration = librosa.core.get_duration(y, sr=sr)
times = np.linspace(1/sr, duration, sr*duration)
print duration
print sr
print len(y)
print len(times)

y_harmonic, y_percussive = librosa.effects.hpss(y)
C = librosa.feature.chroma_cqt(y=y_harmonic, sr=sr, n_chroma=10)
print len(C)
print len(C[0])
np.savetxt("chromagram.csv", C, delimiter=",")

# Make a new figure
plt.figure(figsize=(12,4))

# Display the chromagram: the energy in each chromatic pitch class as a function of time
# To make sure that the colors span the full range of chroma values, set vmin and vmax
librosa.display.specshow(C, sr=sr, x_axis='time', y_axis='chroma', vmin=0, vmax=1)

plt.title('Chromagram')
plt.colorbar()

plt.tight_layout()
plt.show()