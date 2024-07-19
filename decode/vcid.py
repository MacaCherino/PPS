# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 16:37:59 2024

@author: usuario
"""
import numpy as np
import struct
import os

# Definir las constantes
FRAMESIZE    = 892

# funcion para leer encabezado de cada canal virtual
def VC_hdr(frames,wr):
    
    size      = len(frames[0])          # se define cantidad de tramas
    
    # se crean arreglos para almacenar valores de encabezado
    ver     = np.zeros(size,np.uint8)   # Version
    sc_id   = np.zeros(size,np.uint8)   # ID del satelite
    vc_id   = np.zeros(size,np.uint8)   # ID del canal virtual
    counter = np.zeros(size,np.uint32)  # Contador
    replay  = np.zeros(size,np.uint8)   # Replay Flag
    spare   = np.zeros(size,np.uint8)   # Spare
    vc_hdr  = []                        # encabezado
    
    for i in range (0,size):                # se recorren todas las tramas
        frame = frames[:,i]                 # se toma una trama
        hdr   = frame[0:6]                  # se toman los primeros 6 bytes que corresponden al encabezado
        hdr   = np.ascontiguousarray(hdr)
        
        ver[i]     = ( struct.unpack(">H", hdr[:2])[0]&(0xC000))  >>14  # los primeros 2 bits son la version
        sc_id[i]   = ( struct.unpack(">H", hdr[:2])[0]&(0x3FC0))  >> 6  # los siguientes 8 bits son el id del satelite
        vc_id[i]   =   struct.unpack(">H", hdr[:2])[0]&(0x3F)           # los siguientes 6 bits son el id del canal virtual
        counter[i] = ((struct.unpack(">H", hdr[2:4])[0]&(0xFFFF)) << 16 | (struct.unpack(">H", hdr[4:])[0]&(0xFF00))) >> 8  # los siguientes 24 son el contador
        replay[i]  = ( struct.unpack(">H", hdr[4:])[0]&(0x80))    >> 7  # el siguiente bit es la replay flag
        spare[i]   = ( struct.unpack(">H", hdr[4:])[0]&(0x7F))          # los ultimos 7 bits son el spare
        
        if not (vc_id[i] == 63):        # si el ID de canal virtual no es 63, no se trata de un paquete de relleno
            vc_hdr.append( {
                "version"    : ver    [i],
                "sc_id"      : sc_id  [i],
                "vc_id"      : vc_id  [i],
                "counter"    : counter[i],
                "replay_flag": replay [i],
                "spare"      : spare  [i] 
                })
            if wr:                      # si la escritura esta habilitada se escribe la trama con su correspondiente canal virtual
                write_channel(frame,FRAMESIZE,vc_id[i])
                
        
    return ver,sc_id,vc_id,counter,replay,spare,vc_hdr
    
# funcion para almacenar los datos de cada canal virtual
def write_channel(data, size, vcid):
    # Crear el nombre del archivo
    filename = f"files/test3/channels/channel_{vcid}.bin"
    data = np.ascontiguousarray(data[:size])
    # Abrir el archivo en modo "a+" (anadir y leer)
    with open(filename, "ab") as f:
        # Escribir los datos en el archivo
        f.write(data)

def main():
    # se extraen las tramas corregidas
    rs_out = np.fromfile(open('files/test3/rs_out.bin',"rb"), dtype=np.uint8)
    size = len(rs_out)//FRAMESIZE   # se define la cantidad de tramas
    # se reacomodan los datos extraidos por tramas
    frames = np.zeros((FRAMESIZE,size),np.uint8)
    for i in range(0,FRAMESIZE):
        frames[i,:]=rs_out[i*size:(i+1)*size]
        
    # Crear el directorio si no existe
    os.makedirs("files/test3/channels", exist_ok=True)

    # Obtener la lista de archivos en el directorio "channels"
    files = os.listdir("files/test3/channels")

    # Eliminar todos los archivos en el directorio "channels"
    for file in files:
        os.remove(os.path.join("files/test3/channels", file))
    
    ver,sc_id,vc_id,counter,replay,spare,vc_hdr = VC_hdr(frames,1)  # obtener el encabezado de cada canal virtual

    return vc_hdr,counter,vc_id

if __name__ == "__main__":
    vc_hdr,counter,vc_id = main()
