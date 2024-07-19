from viterbi import *
import numpy as np
from alignFrame import syncFrame

k = 7
n = 2
m = 1 
n_state_bits = m*(k-1)

polynomials = [0x4f, 0x6d]
n_polynomials = len(polynomials)

transitions = Transitions(polynomials)

# Definir las constantes
FRAMESIZE          = 1024
SYNCWORDSIZE       = 32
FRAMEBITS          = (FRAMESIZE * 8)
CODEDFRAMESIZE     = (FRAMEBITS * 2)
CSIZE              = 16
SYNCWORDSIZEDOUBLE = (SYNCWORDSIZE * 2)

def conv_decode(data):
    decoded = transitions.decode(data)
    num_decoded = decoded.num
    len_decoded = decoded.len
    decoded_out = np.zeros(len_decoded)
    for i in range(0,len_decoded):
        decoded_out[i] = not ((num_decoded>>(len_decoded-1-i)) & 1)
   
    return decoded_out, decoded

def convert_to_decimal(frame):
    out = 0
    for i in range(0,len(frame)):
        out = (out<<1) | int(frame[i])
    return out

def viterbi(frame):
    coded_original = syncFrame(frame)                   # se extraen los 16384 bits que conforman cada trama alineada
    size = np.shape(coded_original)[1]                  # se define la cantidad de tramas
    viterbi_out = np.zeros((FRAMEBITS,size),np.uint8)   # se define arreglo para almacenar las tramas decodificadas
    # se recorren todas las tramas
    for i in range (0,size):                        
        frame_i = coded_original[:,i]               # se toma una trama
        data_decimal = convert_to_decimal(frame_i)  # se la convierte a decimal para poder emplear el algoritmo
        data = BinData()                            # clase utilizada para manejar secuencias largas de datos binarios 
        data.len = len(coded_original)              
        data.num = data_decimal
    
        decodedbits,decodedstream = conv_decode(data)   # se aplica la decodificacion convolucional
        viterbi_out[:,i] = decodedbits                  # se almacena la trama decodificada
        print(f'Decodificacion Viterbi en trama {i+1}/{size}')
    
    return viterbi_out

def main():
    # se extraen los datos del slicer
    frame = np.fromfile(open('files/test3/demod_slc.bin', "rb"), dtype=np.uint8)
    decoded = viterbi(frame)
    return decoded

if __name__ == "__main__":
    decoded = main()
    # se almacenan los datos decodificados en un archivo .bin
    decoded.tofile('files/test3/viterbi_out.bin')
