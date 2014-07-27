#
# Calling CANLIB from Python
#
# Requires Python 2.5, or Python 2.3/2.4 with ctypes installed.
# Has been tested with Python 2.5.
# You can get ctypes here: http://starship.python.net/crew/theller/ctypes
#

from ctypes import *

# For sleep()
import time


# -------------------------------------------------------------------------
# dll initialization
# -------------------------------------------------------------------------
# Load canlib32.dll
canlib32 = windll.canlib32

# Load the API functions we use from the dll
canInitializeLibrary = canlib32.canInitializeLibrary
canOpenChannel = canlib32.canOpenChannel
canBusOn = canlib32.canBusOn
canBusOff = canlib32.canBusOff
canClose = canlib32.canClose
canWrite = canlib32.canWrite
canRead = canlib32.canRead
canReadSpecific = canlib32.canReadSpecific
canGetChannelData = canlib32.canGetChannelData
canGetErrorText = canlib32.canGetErrorText
canReadSyncSpecific = canlib32.canReadSyncSpecific

RTR = 0x0001

# A few constants from canlib.h
canCHANNELDATA_CARD_FIRMWARE_REV = 9
canCHANNELDATA_DEVDESCR_ASCII = 26


# Define a type for the body of the CAN message. Eight bytes as usual.
MsgDataType = c_uint8 * 8

# Initialize the library...
canInitializeLibrary()

# ... and open channels 0 and 1. These are assumed to be on the same
# terminated CAN bus.
#for h = arange(3,2000)
stat = -1
h = 0

cells = arange(1,107)


rx_msg = MsgDataType()
rx_id = c_long()
rx_dlc = c_int()
rx_flags = c_int()
rx_time = c_long()


while stat < 0 or h > 300:
    hnd1 = canOpenChannel(c_int(h), c_int(32))

# Go bus on
    stat = canBusOn(c_int(hnd1))
    print h
    h = h + 1

# Setup a message
msg = MsgDataType()


i = 2
j = 3
can_id = arange(788,811)
k = 0
for i in can_id:
    print i
    rx_id = c_long(i)
    stat = canWrite(c_int(hnd1), c_int(i), pointer(msg), c_int(8), c_int(RTR))
    if stat < 0:
        print stat
        assert(0)
    
    stat  = canReadSyncSpecific(c_int(hnd1),c_int(i), c_ulong(10))
    #print stat
    #stat = canReadSpecific(c_int(hnd1), pointer(rx_id), pointer(rx_msg),pointer(rx_dlc), pointer(rx_flags), pointer(rx_time))
    rx_id = c_long(0)    
    while rx_id != i:    
        stat = canRead(c_int(hnd1), pointer(rx_id), pointer(rx_msg),pointer(rx_dlc), pointer(rx_flags), pointer(rx_time))

    print rx_id
    if stat < 0 and stat != -2:
        print stat
        assert(0)
    if stat == -2:
        print "missing"
    
    cells[k] = (rx_msg[1] << 8 | rx_msg[0])
    k = k + 1
    cells[k] = (rx_msg[3] << 8 | rx_msg[2])
    k = k + 1
    
    if i != 797: #half pad    
        cells[k] = (rx_msg[5] << 8 | rx_msg[4])
        k = k + 1
        cells[k] = (rx_msg[7] << 8 | rx_msg[6])
        k = k + 1
    
    print repr(c_long(rx_msg[0])) + ',' + repr(rx_msg[1]) + ',' + repr(rx_msg[2]) + ',' + repr(rx_msg[3]) + ',' + repr(rx_msg[4]) + ',' + repr(rx_msg[5]) + ',' + repr(rx_msg[6]) + ',' + repr(rx_msg[7])

bar(arange(1,107), cells)
out = np.column_stack((arange(1,107),cells/1000.0))
np.savetxt('cells_' + time.strftime("%Y-%m-%d_%H_%M_%S", time.gmtime()) + ".csv" , out, delimiter=",", fmt = '%1.8f')
print "done"
print max(cells)
print min(cells)
# Some cleanup, which would be done acutomatically when the DLL unloads.
stat = canBusOff(c_int(hnd1))

canClose(c_int(hnd1))


