import numpy as np

# Definir las constantes
FRAMESIZE = 1024
SYNCWORDSIZE = 32
FRAMEBITS = (FRAMESIZE * 8)
CODEDFRAMESIZE = (FRAMEBITS * 2)
CSIZE = 16
SYNCWORDSIZEDOUBLE = (SYNCWORDSIZE * 2)

# funcion para decodificar una trama
def decDiff(frame):                 
    decodedframe=np.zeros(FRAMEBITS)    # se define arreglo para almacenar bits decodificados
    decodedframe[0]=0                   # se define primer bit decodificado en 0
    for i in range(1,FRAMEBITS):        # se recorren los 8192 bits de la trama
        if frame[i-1] == frame[i]:      # si el bit actual es igual al anterior se decodifica el bit como 0
            decodedframe[i]=0           
        else:                           # si el bit actual es no igual al anterior se decodifica el bit como 1
            decodedframe[i]=1
    return decodedframe

# funcion para codificar una trama y realizar comparacion
def encDiff(frame,lastbit):
    codedframe=np.zeros(FRAMEBITS)  # se define arreglo para almacenar trama codificada
    codedframe[0]=lastbit           # se define primer bit de trama codificada
    for i in range(1,FRAMEBITS):    # se recorren los 8192 bits
        if frame[i]!=lastbit:       # si el bit de la trama es distinto al ultimo bit:
            codedframe[i]=1         # se codifica el bit en 1
            lastbit=1               # se actualiza el valor del ultimo bit en 1
        else:                       # si el bit de la trama es igual al ultimo bit:
            codedframe[i]=0         # se codifica el bit en 0
            lastbit=0               # se actualiza el valor del ultimo bit en 0
            
    return codedframe
    
# funcion para comparar la trama codificada original y la codificada luego de decodificarla
def compare(a,b):
    len_a = len(a)
    len_b = len(b)
    
    if len_a!=len_b:    # los tamanos de ambas tramas deben ser iguales para poder ser comparadas
        print("Los tamaños no coinciden")
        return 0
    else:
        for i in range(0,len_a):
            if (a[i]!=b[i]):    # si algun bit es distinto devuelve 0
                return 0
    # si todos los bits coinciden devuelve 1
    return 1

def decoded_frame():
    
    #se extraen las tramas a la salida del decodificador viterbi
    viterbi_out = np.fromfile(open('files/test3/viterbi_out.bin',"rb"), dtype=np.uint8)         # se extraen los 8192 bits que conforman la trama a la salida de la decodifiacion viterbi
    size = len(viterbi_out)//FRAMEBITS              # se define la cantidad de tramas decodificadas
    # se reacomodan los datos extraidos por tramas
    frames = np.zeros((FRAMEBITS,size),np.uint8)
    for i in range(0,FRAMEBITS):
        frames[i,:]=viterbi_out[i*size:(i+1)*size]
        
    nrz_out = np.zeros((FRAMEBITS,size),np.uint8)   # se define arreglo para almacenar las tramas decodificadas diferencialmente
    for i in range(0,size):             # se recorren todas las tramas
        frame = frames[:,i]             # se toma una trama
        decodedbits = decDiff(frame)    # se aplica la decodificacion diferencial
        nrz_out[:,i] = decodedbits      # se almacenan los datos decodificados
    
    return nrz_out
    
def main():
    decoded = decoded_frame()
    
    return decoded

if __name__ == "__main__":
    decoded = main()
    # se almacenan las tramas decodificadas en un archivo .bin
    decoded.tofile('files/test3/nrz_out.bin')


    