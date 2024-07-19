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

def alignFrame(pos,frame,size):
    frame_out = np.zeros((CODEDFRAMESIZE,size),np.uint8)    # se define arreglo para almacenar la trama alineada
    # se recorren todas las tramas y se las desplaza "pos" veces
    for i in range (0,size):
        frame_out[:,i] = frame[pos+i*CODEDFRAMESIZE:pos+(i+1)*CODEDFRAMESIZE]
    return frame_out

def syncFrame(frame):
    size_total = len(frame)//CODEDFRAMESIZE-1        # definir cantidad de tramas
    frame_align = alignFrame(13257,frame,size_total) # alinear la trama pasando como parametro la ubicacion de la SW obtenida
    #test3 usar 13257
    #test1 usar 2056
    
    return frame_align

def main():
    # se extraen los datos del slicer
    data_file = np.fromfile(open('files/test3/demod_slc.bin', "rb"), dtype=np.uint8)
    data  = syncFrame(data_file)
    # se almacena la trama alineada en un archivo .bin
    data.tofile('files/test3/frame_sync.bin')
    return data
    
if __name__ == "__main__":
    data=main()
    