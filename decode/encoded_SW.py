def parity(x):
    return bin(x).count('1') % 2

def conv_enc(syncword):
    polys               = [0x4f, 0x6d]      # definir polinomios generadores

    encodedWord         = 0                 # inicializar palabra codificada de salida en 0

    encstate            = 0                 # incializar estado de codificacion en 0
    wordSize            = 4                 # inicializar tamano de la palabra en 4 bytes
    processedBytes      = 0                 # inicializar cantidad de bytes procesados en 0
    encodedWordPosition = 63                # inicializar posicion del ultimo bit codificado en 63
    
    while processedBytes < wordSize:                    # se recorren todos los bytes de la palabra de sincronizacion
        c = syncword[processedBytes]                    # se toma un byte de la palabra
        for i in range(7, -1, -1):                      # se recorren los 8 bits del byte
            encstate = (encstate << 1) | ((c >> 7) & 1) # se calcula el nuevo estado desplazando una posicion el ultimo estado y agregando el bit mas significativo del byte
            c      <<= 1                                # se desplaza una posicion a la izquierda el byte que se esta codificando

            # Codificacion de Palabra
            encodedWord         |= (1 - parity(encstate & polys[0])) << encodedWordPosition
            encodedWord         |= (1 - parity(encstate & polys[1])) << (encodedWordPosition - 1)
            encodedWordPosition -= 2                    # se actualiza posicion del ultimo bit codificado
            
        processedBytes += 1                             # se actualiza la cantidad de bytes procesados
        
    return encodedWord

def nrz_enc(syncword):

    encodedWord         = 0         # inicializar palabra codificada de salida en 0

    wordSize            = 4         # inicializar tamano de la palabra en 4 bytes
    processedBytes      = 0         # inicializar cantidad de bytes procesados en 0
    encodedWordPosition = 31        # inicializar posicion del ultimo bit codificado en 31
    last_bit            = 0         # inicializar valor de ultimo bit en 0
    actual_bit          = 0         # inicializar valor de bit actual en 0
    
    while processedBytes < wordSize:        # se recorren todos los bytes de la palabra de sincronizacion
        c = syncword[processedBytes]        # se toma un byte de la palabra
        for i in range(7, -1, -1):          # se recorren los 8 bits del byte
            actual_bit = ((c >> 7) & 1)     # se toma el bit mas significativo no codificado
            c        <<= 1                  # se desplaza una posicion a la izquierda el byte que se esta codificando
            if (last_bit != actual_bit):    # si el bit actual es distinto al anterior
                encodedWord |= 1 << encodedWordPosition     # se codifica el bit de salida en 1
                last_bit     = 1                            # se actualiza el valor del ultimo bit
            else:                           # si el bit actual igual al anterior
                encodedWord |= 0 << encodedWordPosition     # se codifica el bit de salida en 0
                last_bit     = 0                            # se actualiza el valor del ultimo bit
            encodedWordPosition -= 1        # se actualiza posicion del ultimo bit codificado
        processedBytes += 1                 # se actualiza la cantidad de bytes procesados
        
    # Convertir encodedWord a bytearray
    encodedWordBytes = encodedWord.to_bytes((encodedWord.bit_length() + 7) // 8, byteorder='big')
    
    return encodedWord, encodedWordBytes


syncword       = bytearray([0x1A, 0xCF, 0xFC, 0x1D])    #definir palabra de sincronizacion
nrz, nrz_bytes = nrz_enc(syncword)                      #codificar la palabra de sincronizacion con nrz-m
encSW          = conv_enc(nrz_bytes)                    #codificar la palabra convolucionalmente
    
print(f"Encoded Word NRZ: 0x{nrz:08x}")
print(f"Encoded Word NRZ + Conv: 0x{encSW:016x}")
    


