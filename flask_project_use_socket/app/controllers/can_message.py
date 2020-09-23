import sys
from canlib import canlib, Frame
import _thread
import time

def init(channel_number = 0,bitrate = 500):
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
    # Open CAN channel, virtual channels are considered ok to use
    ch = canlib.openChannel(channel_number, canlib.canOPEN_ACCEPT_VIRTUAL)
    ch.iocontrol.local_txecho = False
    print("Setting bitrate to 500 kb/s")
    ch.setBusParams(canlib.canBITRATE_500K)
    # print("Going on bus")
    # ch.busOn()
    return ch
    
def sendMessage(ch,frame = Frame(id_=0x79D,
                data=[0x02,0x10, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00],
                dlc=8,
                flags=0)):
    ch.write(frame)

def getMessage(ch):
    frame = ch.read(timeout=500)
    # print("{id:02x}  {dlc}  {data}  {timestamp}".format(
    #     id=frame.id,
    #     dlc=frame.dlc,
    #     data=' '.join('%02x' % i for i in frame.data),
    #     timestamp=frame.timestamp
    # ))
    return str("{id:02x}  {dlc}  {data}  {timestamp}".format(
        id=frame.id,
        dlc=frame.dlc,
        data=' '.join('%02x' % i for i in frame.data),
        timestamp=frame.timestamp
    ))

def run(ch):
    print("Going on bus")
    ch.busOn()
    return ch

def stop(ch):
    ch.busOff()
    ch.close()

# if __name__ == "__main__":
#     ch = init()
#     run(ch)