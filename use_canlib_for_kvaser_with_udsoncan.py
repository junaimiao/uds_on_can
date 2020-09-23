from can.interfaces.vector import VectorBus
from udsoncan.connections import PythonIsoTpConnection
from udsoncan.client import Client
import isotp

import sys
from canlib import canlib, Frame

#######################
channel_number = 0
# Specific CANlib channel number may be specified as first argument
if len(sys.argv) == 2:
    channel_number = int(sys.argv[1])

print("Opening channel %d" % (channel_number))
# Use ChannelData to get some information about the selected channel
chd = canlib.ChannelData(channel_number)
print("%d. %s (%s / %s) " % (channel_number,
                             chd.channel_name,
                             chd.card_upc_no,
                             chd.card_serial_no))

# If the channel have a custom name, print it
# if chd.custom_name != '':
    # print("Customized Channel Name: %s " % (chd.custom_name))

# Open CAN channel, virtual channels are considered ok to use
ch = canlib.openChannel(channel_number, canlib.canOPEN_ACCEPT_VIRTUAL)

#Add by hzc
ch.iocontrol.local_txecho = False

print("Setting bitrate to 500 kb/s")
ch.setBusParams(canlib.canBITRATE_500K)

# print("Going on bus")
# ch.busOn()
#######################

# Refer to isotp documentation for full details about parameters
isotp_params = {
   'stmin' : 32,                          # Will request the sender to wait 32ms between consecutive frame. 0-127ms or 100-900ns with values from 0xF1-0xF9
   'blocksize' : 8,                       # Request the sender to send 8 consecutives frames before sending a new flow control message
   'wftmax' : 0,                          # Number of wait frame allowed before triggering an error
   'll_data_length' : 8,                  # Link layer (CAN layer) works with 8 byte payload (CAN 2.0)
   'tx_padding' : 0,                      # Will pad all transmitted CAN messages with byte 0x00. None means no padding
   'rx_flowcontrol_timeout' : 1000,        # Triggers a timeout if a flow control is awaited for more than 1000 milliseconds
   'rx_consecutive_frame_timeout' : 1000, # Triggers a timeout if a consecutive frame is awaited for more than 1000 milliseconds
   'squash_stmin_requirement' : False     # When sending, respect the stmin requirement of the receiver. If set to True, go as fast as possible.
}

# bus = VectorBus(channel=0, bitrate=9600)                                          # Link Layer (CAN protocol)
tp_addr = isotp.Address(isotp.AddressingMode.Normal_11bits, txid=0x123, rxid=0x79D) # Network layer addressing scheme
stack = isotp.CanStack(bus=ch., address=tp_addr, params=isotp_params)               # Network/Transport layer (IsoTP protocol)
conn = PythonIsoTpConnection(stack)                                                 # interface between Application and Transport layer
with Client(conn, request_timeout=1) as client:                                     # Application layer (UDS protocol)
   client.change_session(1)