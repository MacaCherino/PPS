import numpy as np
import struct
from vcid import VC_hdr

# Definir las constantes
FRAMESIZE    = 892

SEQUENCE_FLAG_MAP = {
  0: "Continued Segment",
  1: "First Segment",
  2: "Last Segment",
  3: "Single Data"
}

# funcion para leer encabezado de paquetes de datos
def ParseMSDU(data):
    
    data    = np.ascontiguousarray(data)
    
    o       = struct.unpack(">H", data[:2])[0]
    version = (o & 0xE000) >> 13    # los primeros 3 bits son la version
    type    = (o & 0x1000) >> 12    # el siguiente bit es el tipo
    shf     = (o & 0x800)  >> 11    # el siguiente bit es la bandera de encabezado secundario
    apid    = (o & 0x7FF)           # los siguientes 11 bits es el APID

    o            = struct.unpack(">H", data[2:4])[0]
    sequenceflag = (o & 0xC000) >> 14                   # los siguientes 2 bits son la bandera de secuencia
    packetnumber = (o & 0x3FFF)                         # los siguientes 14 bits son el contador de secuencia de paquete
    packetlength = struct.unpack(">H", data[4:6])[0] -1 # los ultimos 16 bits son la longiutud de paquete
    
    data         = data[6:]         # se elimina el encabezado del paquete de datos
    
    return version, type, shf, apid, sequenceflag, packetnumber, packetlength, data

# funcion para leer encabezado del CVCDU
def cvcdu_hdr(frames):
    
    total_frames = len(frames[0])               # se determina la cantidad de tramas
    
    spare = np.zeros(total_frames,np.uint8)     # se define arreglo para almacenar el valor de spare
    fhp   = np.zeros(total_frames,np.uint16)    # se define arreglo para almacenar el valor del first header pointer

    for i in range (0,total_frames):        # se recorren todas las tramas
        frame = frames[:,i]                 # se toma una trama
        hdr   = frame[:2]                   # se toman los primeros 2 bytes que conforman el encabezado del canal de datos
        hdr   = np.ascontiguousarray(hdr)
        
        spare[i] = (struct.unpack(">H", hdr)[0]&(0xF800)) >> 11 # los primeros 5 bits son el spare
        fhp  [i] = (struct.unpack(">H", hdr)[0]&(0x07FF))       # los ultimos 11 bits son el first header pointer
        
    return spare, fhp

# funcion para verificar si el header es valido
def check_hdr(apid,vcid,version,type,packetlength,len_data):
    #un encabezado de datos es valido si:
    #vcid es el resultado entero de la division de apid y 32
    vcid_check = (apid//32 == vcid)
    #apid es menor a 2016
    apid_check = apid < 2016
    #version es 0
    ver_check = version == 0
    #type es 0
    type_check = type == 0
    #si packetlength es menor a 8192
    length_check = packetlength<8192
    
    if (vcid_check and apid_check and ver_check and type_check and length_check):
        return 1
    else:
        return 0
    
# funcion para agregar datos en un arreglo
def append_data(start,packet,packet_out):
    
    bytes_frame = len(packet)                        # se define la longitud del paquete en bytes
    packet_out[start:bytes_frame+start] = packet[:]  # se copian los datos del paquete en el arreglo a partir de la posicion del ultimo dato almacenado
    
    return packet_out

# funcion para almacenar un paquete finalizado
def finish_packet(packet,sequenceflag,packetnumber,last_packet,first_packet,finished_packets,apid,frame):
    
    packet_list = list(packet)
    
    if not apid == 2047:        # si no se trata de un paquete de relleno se determina que tipo de paquete es
            
        if sequenceflag == 1:                   # First Segment
            finished_packets = []                   # se inicializa lista para almacenar los datos del paquete
            first_packet     = packetnumber         # se determina el valor del primer paquete
            last_packet      = packetnumber         # se actualiza el valor del ultimo paquete guardado
            finished_packets.append(packet_list)    # se guardan los datos del paquete en la lista
            
        elif sequenceflag == 0:                 # Continued Segment
            if packetnumber == last_packet + 1:     # si el numero del paquete actual es igual al numero del paquete anterior+1 no se salteo ningun paquete
                last_packet  = packetnumber         # se actualiza el valor del ultimo paquete guardado
                finished_packets.append(packet_list)# se guardan los datos del paquete en la lista
            else:   # si el numero del paquete actual no es igual al numero del paquete anterior+1 se salteo un paquete e imprime una advertencia
                print(f'Faltan paquetes entre {last_packet} y {packetnumber}')
                last_packet  = packetnumber
                
        elif sequenceflag == 2:                 # Last Segment
            if packetnumber == last_packet + 1:     # si el numero del paquete actual es igual al numero del paquete anterior+1 no se salteo ningun paquete
                print(f'Guardando paquetes de {first_packet} a {packetnumber}')
                                                    # se define el nombre del archivo a partir del numero del primer paquete
                filename = f'files/test3/packets/packet_{first_packet}'
                finished_packets.append(packet_list)# se guardan los datos del paquete en la lista
                write_bin(finished_packets,filename)# se escriben los datos del paquete en un archivo
            else:   # si el numero del paquete actual no es igual al numero del paquete anterior+1 se salteo un paquete e imprime una advertencia
                print(f'Faltan paquetes entre {last_packet} y {packetnumber}')
                last_packet = packetnumber
                
        elif sequenceflag == 3:                 # Single Data
                                                    # se escriben los datos del paquete en un archivo
            packet.tofile(f'files/test3/packets/packet_{packetnumber}')
    else:   # si se trata de un paquete de relleno se descarta el paquete e imprime un mensaje
        print('Paquete de relleno descartado')
    return last_packet,first_packet,finished_packets

# Funcion para almacenar los datos que conforman el paquete
def write_bin(packets,filename):
    print(f'Paquete almacenado en {filename}')
    with open(filename, 'wb') as f:
        for packet in packets:
            f.write(struct.pack('I', len(packet)))
            for item in packet:
                f.write(struct.pack('B', item))

def main():
    # se extraen los datos del canal virtual 1, correspondiente a imagenes de mesoescala
    vc_1         = np.fromfile(open('files/test3/channels/channel_1.bin',"rb"), dtype=np.uint8)
    total_frames = len(vc_1)//FRAMESIZE   # se define la cantidad de tramas
    # se reacomodan los datos extraidos por tramas
    frames       = np.zeros((FRAMESIZE,total_frames),np.uint8)
    for i in range(0,total_frames):
        frames[:,i] = vc_1[i*FRAMESIZE:(i+1)*FRAMESIZE]
     
    # se extraen los encabezados de cada canal virtual
    ver_vc,sc_id_vc,vc_id_vc,counter_vc,replay_vc,spare_vc,vc_hdr = VC_hdr(frames,0)
        
    data      = frames[6:,:]                    # se eliminan los 6 primeros bytes del encabezado del CV
    spare,fhp = cvcdu_hdr(data)                 # se extrae el encabezado de la unidad de datos (primeros 2 bytes)
    data      = data[2:,:]                      # la zona de paquete de datos se encuentra en los siguientes 884 bytes
    
    # Inicializacion de variables
    last_pos     = 0                            # se inicializa la ultima posicion del paquete en 0
    packetnumber = 0                            # se inicializa el numero de paquete en 0
    sequenceflag = 0                            # se inicializa bandera de secuencia en 0
    last_packet  = 0                            # se inicializa el ultimo numero de paquete en 0
    first_packet = 0                            # se inicializa el primer numero de paquete en 0
    apid         = 0                            # se inicializa el apid en 0
    
    # Inicializacion de banderas
    pending_packet = 0                          # se establece que no hay paquetes pendientes
    incomplete     = 0                          # se establece que no hay paquetes incompletos
    
    # Inicializacion de arreglos/listas
    packet_arr       = np.zeros(8192,np.uint8)  # se define arreglo para almacenar los bytes de un paquete (maximo 8192 bytes)
    inc_bytes        = np.zeros(6,np.uint8)     # se define arreglo para almacenar bytes de un paquete incompleto
    finished_packets = []                       # se define lista para almacenar un paquete compelto
    
    # se recorren todas las tramas
    for i in range(0,total_frames):
        if not (fhp[i] == 2047):    # se encontro un encabezado de paquete
            pointer          = fhp[i]           # fhp indica el offset desde donde comienza el paquete de datos
            start_new_packet = data[pointer:,i] # se desplaza la trama para indicar el inicio de un nuevo paquete
            end_prev_packet  = data[:pointer,i] # se toman los valores anteriores para indicar los ultimos datos del paquete anterior
            
            # Se procesa el paquete previo
            if pending_packet:      # si hay un paquete no finalizado
                if not incomplete:      # si el inicio del paquete anterior tenia suficientes bytes para representar un encabezado
                    packet_arr     = append_data(last_pos, end_prev_packet, packet_arr) # se agregan completan los datos del paquete pendiente
                    pending_packet = 0                                                  # se indica que no hay paquetes pendientes
                    # se almacena el paquete finalizado
                    last_packet,first_packet,finished_packets=finish_packet(packet_arr,sequenceflag,packetnumber,last_packet,first_packet,finished_packets,apid,i)
                else:  # si el inicio del paquete anterior no tenia suficientes bytes para representar un encabezado, continua en el paquete actual
                    len_pack_inc = len(inc_bytes) + len(end_prev_packet)    # la longitud del nuevo paquete es la cantidad de bytes que conformaban el paquete anterior y el actual
                    if len_pack_inc >= 6:                                   # si la longitud del paquete tiene suficientes bytes para representar un encabezado
                        complete_pack = np.zeros(len_pack_inc,np.uint8)         # se define un arreglo para almacenar los datos y encabezado del paquete completo
                        complete_pack = append_data(0,inc_bytes,complete_pack)
                        complete_pack = append_data(len(inc_bytes),end_prev_packet,complete_pack)
                        # se lee el encabezado del paquete
                        version, type, shf, apid, sequenceflag, packetnumber, packetlength, data_o = ParseMSDU(complete_pack) 
                        total_length  = packetlength + 2                        # se cuenta con 2 bytes adicionales de CRC
                        packet_arr    = np.zeros(total_length,np.uint8)         # se define arreglo para almacenar los datos del paquete completo
                        packet_arr    = append_data(0,data_o,packet_arr)        # se copian los datos en el arreglo
                        # se almacena el paquete finalizado
                        last_packet,first_packet,finished_packets=finish_packet(packet_arr,sequenceflag,packetnumber,last_packet,first_packet,finished_packets,apid,i)
                    incomplete = 0  # se indica que no hay encabezados incompletos
            
            # Se procesa el nuevo paquete
            if len(start_new_packet) >= 6:   # si la longitud del paquete tiene suficientes bytes para representar un encabezado
                # se lee el encabezado del paquete    
                version, type, shf, apid, sequenceflag, packetnumber, packetlength, data_o = ParseMSDU(start_new_packet) 
                if not (apid == 2047):      # si no se trata de un paquete de relleno
                    total_length = packetlength + 2                 # se cuenta con 2 bytes adicionales de CRC
                    packet_arr   = np.zeros(total_length,np.uint8)  # se define arreglo para almacenar los datos del paquete completo
                    
                    while total_length < len(start_new_packet): # si la longitud del paquete es menor a la longitud de la trama, se tienen varios paquetes en una misma trama
                        
                        packet_arr     = data_o[:total_length]  # de toman los datos hasta la longitud correspondiente
                        pending_packet = 0                      # se indica que no hay paquetes pendientes
                        # se almacena el paquete finalizado
                        last_packet,first_packet,finished_packets=finish_packet(packet_arr,sequenceflag,packetnumber,last_packet,first_packet,finished_packets,apid,i)
                        start_new_packet = data_o[total_length:]# se toma un nuevo paquete
                        if len(start_new_packet)>=6:    # si la longitud del paquete tiene suficientes bytes para representar un encabezado
                            # se lee el encabezado del paquete
                            version, type, shf, apid, sequenceflag, packetnumber, packetlength, data_o = ParseMSDU(start_new_packet) 
                            total_length = packetlength + 2                 # se cuenta con 2 bytes adicionales de CRC
                            packet_arr   = np.zeros(total_length,np.uint8)  # se define arreglo para almacenar los datos del paquete completo
                        else:   # si el paquete no tiene suficientes bytes para representar un encabezado, continua en el siguiente paquete
                            incomplete     = 1                  # se indica que el paquete esta incompleto
                            pending_packet = 1                  # se indica que hay un paquete pendiente
                            inc_bytes      = start_new_packet   # se guardan los bytes del paquete incompelto
                            
                    if not incomplete:      # si el paquete tenia suficientes bytes para representar un encabezado
                        packet_arr     = append_data(0,data_o,packet_arr)   # se copian los datos de la trama al inicio del paquete
                        pending_packet = 1                                  # se indica que hay un paquete pendiente
                        last_pos       = len(data_o)                        # se guarda la posicion donde se almaceno el ultimo dato
                else:   # si el paquete es de relleno se descarta e imprime un mensaje
                    print('Paquete de relleno descartado')
            else:   # si la longitud del paquete tiene suficientes bytes para representar un encabezado, continua en el siguiente paquete
                incomplete     = 1                  # se indica que el paquete esta incompleto
                pending_packet = 1                  # se indica que hay un paquete pendiente
                inc_bytes      = start_new_packet   # se guardan los bytes del paquete incompelto
        else:   # si fhp = 2047 el paquete es la continuacion del anterior y no contiene encabezado de datos
            data_cont = data[:,i]   # se toma toda una trama, ya que la trama solo contiene datos
            if pending_packet:      # si hay un paquete pendiente
                if not incomplete:  # si el paquete anterior tenia suficientes bytes para representar un encabezado
                    packet_arr = append_data(last_pos, data_cont, packet_arr)   # se copian los datos de la trama a partir de la posicion del ultimo dato almacenado
                    last_pos   = last_pos+len(data_cont)                        # se guarda la posicion donde se almaceno el ultimo dato
                else:               # si el paquete anterior no tenia suficientes bytes para representar un encabezado, continua en el paquete actual
                    len_pack_inc   = len(inc_bytes) + len(data_cont)                    # la longitud del nuevo paquete es la cantidad de bytes que conformaban el paquete anterior y el actual
                    complete_pack  = np.zeros(len_pack_inc,np.uint8)                    # se define un arreglo para almacenar los datos y encabezado del paquete completo
                    complete_pack  = append_data(0,inc_bytes,complete_pack)
                    complete_pack  = append_data(len(inc_bytes),data_cont,complete_pack)
                    # se lee el encabezado del paquete
                    version, type, shf, apid, sequenceflag, packetnumber, packetlength, data_o = ParseMSDU(complete_pack)
                    total_length   = packetlength + 2                   # se cuenta con 2 bytes adicionales de CRC
                    packet_arr     = np.zeros(total_length,np.uint8)    # se define arreglo para almacenar los datos del paquete completo
                    packet_arr     = append_data(0,data_o,packet_arr)   # se copian los datos de la trama al inicio del paquete
                    last_pos       = len(data_o)                        # se guarda la posicion donde se almaceno el ultimo dato
                    incomplete     = 0                                  # se indica que no hay paquetes incompeltos
                    pending_packet = 1                                  # se indica que hay un paquete pendiente
    
    filename = f'files/test3/packets/packet_{first_packet}'
    print(f'Guardando paquetes de {first_packet} a {packetnumber}')
    write_bin(finished_packets,filename)                

if __name__ == "__main__":
    main()
