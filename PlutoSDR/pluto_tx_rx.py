import numpy as np
import adi

#%% Create transmit waveform
# Leer el archivo .wav
samples = np.fromfile('tx.iq', np.complex128)
samples = samples/32768 # convert to -1 to +1
size_total = np.size(samples)
size = size_total//8
num_samps = size  # Numero de muestras por llamada a rx()

#%%
it=1                    # numero de iteracion, cambiar entre 1 a 8
filename=f'rx{it}.iq'
inicio=(it-1)*size
final=size*it-1
samples_tx=samples[inicio:final] # Despues hay que multiplicarlas por 2**14

#%% Parametros de configuracion
sample_rate = 2e6  # Hz
center_freq = 1694.1e6  # Hz

#%%  Create the radio object
Uri = "ip:192.168.2.1" 
sdr = adi.Pluto(Uri)

#%% Parameters of the SDR
Uri = Uri
Loopback = 0                # 0=Disabled, 1=Digital, 2=RF
SamplingRate = sample_rate  # Sample rate of the RX and TX paths[Samples/Sec]

TxLOFreq   = center_freq   # Carrier frequency of TX path [Hz]
TxAtten    = -20           # Attenuation applied to TX path (valid range is -89 to 0 dB [dB])
TxRfBw     = sample_rate   # Bandwidth of front-end analog filter of TX path [Hz]

RxLOFreq        = TxLOFreq    # Carrier frequency of RX path [Hz]
GainControlMode = 'manual'    # Receive path AGC Options: slow_attack, fast_attack, manual
RxHardwareGain  = 30          # Gain applied to RX path (0 to 90 dB). Only applicable when gain_control_mode is set to 'manual'
RxRfBw          = TxRfBw      # Bandwidth of front-end analog filter of RX path [Hz]
RxBufferSize    = num_samps

#%% Config SDR
sdr.loopback = Loopback
sdr.sample_rate = int (SamplingRate)  # Sample rate RX and TX paths[Samples/Sec]

sdr.tx_rf_bandwidth = int(TxRfBw)   # Bandwidth of front-end analog filter of TX path [Hz]
sdr.tx_hardwaregain_chan0 = TxAtten # Attenuation applied to TX path, valid range is -90 to 0 dB [dB]
sdr.tx_lo = int(TxLOFreq)

sdr.rx_rf_bandwidth = int(RxRfBw)  # Bandwidth of front-end analog filter of RX path [Hz]
sdr.gain_control_mode_chan0 = GainControlMode # Receive path AGC Options: slow_attack, fast_attack, manual
sdr.rx_hardwaregain_chan0 = RxHardwareGain # Gain applied to RX path.
sdr.rx_lo = int(RxLOFreq) # Carrier frequency of RX path [Hz]
sdr.rx_buffer_size = RxBufferSize

sdr.tx_cyclic_buffer = True # Enable cyclic buffers
sdr.rx_cyclic_buffer = False

#%% Start the transmitter
sdr.tx(samples_tx*2**14) # start transmitting

#%% Clear buffer just to be safe
for i in range (0, 10):
    raw_data = (sdr.rx())/2**14

# Receive the samples
rxSignal = (sdr.rx())/2**14
#%% Stop the transmission and destroy the radio object
# Since it is not possible to turn off Tx, it is configured to transmit at low power and on a different frequency than Rx.
sdr.tx_destroy_buffer()
sdr.tx_hardwaregain_chan0 = -89
sdr.tx_lo                 = int(2400e6)
sdr.rx_lo                 = int(950e6)

del(sdr) # Destroy the radio object

#%% Guardar las muestras recibidas en un archivo IQ
rxSignal = rxSignal*32768
rxSignal.tofile(filename) # Save to file
