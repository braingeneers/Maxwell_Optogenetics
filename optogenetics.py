import matplotlib.pyplot as plt
import matplotlib as mpl

from scipy import signal
import matplotlib.pyplot as plt

import scipy.sparse as sparse
import scipy
import numpy as np

np.random.seed(42)
#matplotlib.matplotlib_fname()
#plt.style.use('naturefull')

import math

def powerdensity(p_avg_mW, beam_diam_um):
    beam_diameter = beam_diam_um#200 # microns
    average_power = p_avg_mW # 0.5 #122 *10**-3 #25 * 10**-3# mW

    beam_diameter = beam_diameter * 10**-3 #convert to mm
    average_power = average_power # convert to mW

    max_power_density = ((average_power)) / (((beam_diameter/2)**2)* math.pi  )  #[mW/mm²]
    #print(max_power_density, "mW/mm2")
    return max_power_density

def getDACbitvalue(intensity_fraction):
    return int(round(4096 * intensity_fraction))


### Python Array Serial Transfer to Arduino -----------------

import time
import struct
from pySerialTransfer import pySerialTransfer as txfer


def OpenLink(path, baud):
    link = txfer.SerialTransfer(path, baud) #'/dev/cu.usbmodem12401', baud=115200)
    link.open()
    time.sleep(2) # allow some time for the Arduino to completely reset
    base = time.time()
    return link

def StuffObject(txfer_obj, val, format_string, object_byte_size, start_pos=0):
  """Insert an object into pySerialtxfer TX buffer starting at the specified index.

  Args:
    txfer_obj: txfer - Transfer class instance to communicate over serial
    val: value to be inserted into TX buffer
    format_string: string used with struct.pack to pack the val
    object_byte_size: integer number of bytes of the object to pack
    start_pos: index of the last byte of the float in the TX buffer + 1

  Returns:
    start_pos for next object
  """
  val_bytes = struct.pack(format_string, *val)
  for index in range(object_byte_size):
    txfer_obj.txBuff[index + start_pos] = val_bytes[index]
  return object_byte_size + start_pos


def sendDatum(link, sent, format_string_send, format_string_rec):
    time.sleep(2)
    format_size = struct.calcsize(format_string_send)
    StuffObject(link, sent, format_string_send, format_size, start_pos=0)
    link.send(format_size)

    start_time = time.time()
    elapsed_time = 0
    while not link.available() and elapsed_time < 2:
        if link.status < 0:
            print('ERROR: {}'.format(link.status))
        else:
            print('.', end='')
        elapsed_time = time.time()-start_time
    print()

    response =  link.rxBuff[:link.bytesRead]
    #print(response)

    binary_str = bytearray(response)
    #print(binary_str)
    result = struct.unpack(format_string_rec, binary_str)

    #print('SENT: %s' % str(sent))
    #print('RCVD: %s' % str(result))
    #print(' ')


def setArduinoIntensity(intensity_fraction, f_list, link):


    DAC_intensity_bitvalue = int(round(4096 * intensity_fraction))

    print(DAC_intensity_bitvalue)
    print("Expected Voltage:", 5*intensity_fraction)

    data = f_list.copy()
    data.insert(0, DAC_intensity_bitvalue)
    data.append(False) #True: use waveform, False: use intensity
    sent = tuple(data)

    format_string_send = 'H64H?'#64h'
    format_string_rec = 'H64H?'

    sendDatum(link, sent, format_string_send, format_string_rec)


def CloseLink(link): #'/dev/cu.usbmodem112401', baud=115200)
    link.close()
