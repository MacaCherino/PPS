import numpy as np

# Definicion de las palabras de sincronizacion
SW1 = 0xfc4ef4fd0cc2df89
SW2 = 0x03b10b02f33d2076

# Definir las constantes
FRAMESIZE          = 1024
SYNCWORDSIZE       = 32
FRAMEBITS          = (FRAMESIZE * 8)
CODEDFRAMESIZE     = (FRAMEBITS * 2)
CSIZE              = 16
SYNCWORDSIZEDOUBLE = (SYNCWORDSIZE * 2)

# Convertir la palabra de sincronizacion en arreglos de bits
def convertHextoBinary(SW):
    SW_arr = np.zeros(SYNCWORDSIZEDOUBLE)
    for i in range (0,SYNCWORDSIZEDOUBLE):
        SW_arr[i] = (SW>>(SYNCWORDSIZEDOUBLE-i-1))&1
        
    return SW_arr

# Buscar la palabra de sincronizacion
def findSW(SW1, SW2, frame):

    # Inicializacion de cantidad de coincidencias maximas y posicion de SW en 0
    sw1_max = 0
    sw2_max = 0
    sw1_pos = 0
    sw2_pos = 0
    
    # se recorren todos los bits de la trama para encontrar los 64 bits de la SW
    for j in range (0,CODEDFRAMESIZE-64):
        # inicializacion de cantidad de coincidencias en 0
        sw1_count = 0
        sw2_count = 0
        # se recorren 64 bits consecutivos en la trama
        for i in range(0,SYNCWORDSIZEDOUBLE):   
            if frame[i+j]==SW1[i]:
                sw1_count+=1        # si coinciden los bits con la SW se incrementa en 1 la cantidad de coincidencias con SW
            if frame[i+j]==SW2[i]:
                sw2_count+=1        # si coinciden los bits con la SW invertida se incrementa en 1 la cantidad de coincidencias con SW invertida
        # si el contador de coincidencias actual es mayor al maximo se actualiza el valor y posicion de coincidencias maximas
        if sw1_count>sw1_max:
            sw1_max = sw1_count
            sw1_pos = j
        if sw2_count>sw2_max:
            sw2_max = sw2_count
            sw2_pos = j
    
    # se determina si se encontraron mas coincidencias con la SW o la SW invertida
    sw_max  = sw1_max if sw1_max > sw2_max else sw2_max
    sw_pos  = sw1_pos if sw1_max > sw2_max else sw2_pos
    
    return sw_max, sw_pos

def syncFrame(frame):
    
    SW1_arr    = convertHextoBinary(SW1)        # arreglo que contiene la palabra de sincronizacion en bits
    SW2_arr    = convertHextoBinary(SW2)        # arreglo que contiene la palabra de sincronizacion invertida en bits
    size_total = len(frame)//CODEDFRAMESIZE     # cantidad de tramas de 16384 bits
    SW         = np.zeros(size_total)           # arreglo para almacenar la cantidad de coincidencias encontradas
    POS        = np.zeros(size_total)           # arreglo para almacenar la posicion donde se encontro la mayor cantidad de coincidencias
    
    for k in range(0,size_total):               # se recorren todas las tramas
        frame_i    = frame[CODEDFRAMESIZE*k:CODEDFRAMESIZE*(k+1)-1]     # se define una trama constituida por 16384 bits
        SW_i,POS_i = findSW(SW1_arr, SW2_arr, frame_i)                  # se busca la palabra de sincronismo en la trama
        SW[k]      = SW_i                                               # se almacena la cantidad de coincidencias encontradas
        POS[k]     = POS_i                                              # se almacena la ubicacion donde se encontro la mayor cantidad de coincidencias
        print(f'Trama {k+1}/{size_total}')
        
    return frame,SW,POS

def main():
    # se extraen los datos del slicer
    frame = np.fromfile(open('files/test3/demod_slc.bin', "rb"), dtype=np.uint8)
    data,SW,POS = syncFrame(frame)
    return data,SW,POS
    
if __name__ == "__main__":
    data,SW,POS = main()
    SW_result = np.zeros((len(data)//CODEDFRAMESIZE,2),np.uint32)
    SW_result[:,0] = SW
    SW_result[:,1] = POS
    SW_result.tofile('files/test3/sw_pos.bin')
    