import numpy as np
from reed_solomon_ import decode

# Definir las constantes
FRAMESIZE    = 1020
RS_FRAMES    = 4
DATA_BYTES   = 892
PARITY_BYTES = 32
RS_PAR1      = 223
RS_PAR2      = 255 

# funcion para reordenar tramas y eliminar tramas no corregidas
def reord_frames(result,size,status,invalid_frame):
    # se define arreglo para almacenar la cantidad de tramas corregidas
    corrected_frames = np.zeros((FRAMESIZE-RS_FRAMES*PARITY_BYTES,size-invalid_frame),np.uint8)
    j = 0                                                   # se inicilializa en 0 la cantidad de tramas corregidas
    for i in range(0,size):                                 # se recorren todas las tramas
        if not(any(stat == -1 for stat in status[:,i])):    # si la cantidad de errores corregidos no es negativa
            corrected_frames[:,j] = result[:,i]             # se almacena la trama en el arreglo de tramas corregidas
            j = j+1                                         # se incrementa en 1 la cantidad de tramas corregidas
    return corrected_frames        
            

def rs_decode():
    # se extraen las tramas desaleatorizadas
    derand_out = np.fromfile(open('files/test3/derand_out.bin',"rb"), dtype=np.uint8)
    size       = len(derand_out)//(FRAMESIZE)       # se define la cantidad de tramas
    # se reacomodan los datos extraidos por tramas
    frames = np.zeros((FRAMESIZE,size),np.uint8)
    for i in range(0,FRAMESIZE):
        frames[i,:]=derand_out[i*size:(i+1)*size]

    st_out = np.zeros((RS_FRAMES,size))                                 # se define arreglo para almacenar la cantidad de errores corregidos por trama
    r_out  = np.zeros((FRAMESIZE-RS_FRAMES*PARITY_BYTES,size),np.uint8) # se define arreglo para almacenar la trama corregida
    invalid_frame = 0   # se inicializa cantidad de tramas no validas en 0
    
    # se recorren todas las tramas
    for j in range(0,size):                 
        frame     = frames[:,j]                                 # se toma una trama
        frame_lst = list(frame.astype(int))                     # se convierte el arreglo en lista
        st , r    = decode(bytearray(frame_lst),True,RS_FRAMES) # se decodifica la trama con la libreria reed-solomon-ccsds
        print(f'Decodificando trama {j+1}/{size}')
        if any(stat == -1 for stat in st):                      # si alguna trama devuelve una cantidad de errores corregidos negativa:
            st_out[:,j] = st                                    # la trama contiene errores que no se pueden corregir y debe ser descartada
            invalid_frame = invalid_frame+1                     # se incrementa en 1 la cantidad de tramas no validas
            print('La trama contiene errores que no se pueden corregir: Trama descartada')
        else:                                                   # si la cantidad de errores corregidos no es negativa
            st_out[:,j] = st                                    # se almcena la cantidad de errores corregidos
            r_out[:,j]  = list(r)                               # se almacena la trama corregida

    # se reordenan las tramas descartando las no validas
    corrected_frames = reord_frames(r_out, size, st_out,invalid_frame)
        
    return st_out,r_out,corrected_frames


def main():
    status,result,corrected_frames = rs_decode()
    
    return status,result,corrected_frames

if __name__ == "__main__":
    status,result,corrected_frames= main()
    corrected_frames.tofile('files/test3/rs_out.bin')
