import scipy.io.wavfile as wavfile

# Leer el archivo .wav
fs, data = wavfile.read('GOES17HRITCDA.wav')

# Separar los canales I/Q
iq_data = data[:, 0] + 1j * data[:, 1]
iq_data.tofile('tx.iq') # Save to file
