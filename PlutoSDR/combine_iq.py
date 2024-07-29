import numpy as np
import scipy.io.wavfile as wavfile

#%% Crear un arreglo vacio para almacenar los datos combinados
combined_data = np.array([])

# Iterar sobre los 9 archivos .iq
for i in range(1, 9):
    filename = f'rx{i}.iq'  # Nombre del archivo
    data = np.fromfile(filename, np.complex128)  # Cargar datos del archivo
    combined_data = np.concatenate((combined_data, data))  # Concatenar los datos al arreglo combinado

# Guardar los datos combinados en un solo archivo .iq
combined_data.tofile('combined_data.iq')

#%% Cargar los datos IQ combinados desde el archivo .iq
samples = np.fromfile('combined_data.iq', np.complex128)
sample_rate = 2e6  # Hz
N = np.size(samples) # number of samples
wav_samples = np.zeros((N, 2), dtype=np.int16)

wav_samples[...,0] = samples.real
wav_samples[...,1] = samples.imag

wavfile.write('out3.wav', int(sample_rate), wav_samples)
