import sys
# sys.path.append("C:/temp/Canlib_SDK_v5.9/Samples/Python")

# This software is furnished as Redistributable under the Kvaser Software Licence
# https://www.kvaser.com/canlib-webhelp/page_license_and_copyright.html

from canlib import canlib, Frame

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

print("Going on bus")
ch.busOn()

#******* Add by HZC ******#
# print("Sending a message")
# for j in range(10):
#     frame = Frame(id_=0x79D,
#                 data=[0x02,0x10, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00],
#                 dlc=8,
#                 flags=0)
#     ch.write(frame)
#     for k in range(5):
#         frame = ch.read(timeout=500)
#         if frame.id == 0x7dd:
#             print("{id:02x}  {dlc}  {data}  {timestamp}".format(
#                 id=frame.id,
#                 dlc=frame.dlc,
#                 data=' '.join('%02x' % i for i in frame.data),
#                 timestamp=frame.timestamp
#             ))

print("get can message")
while True:
    try:
        frame = ch.read(timeout=50)
        if (frame.flags & canlib.canMSG_ERROR_FRAME != 0):
            # print("***ERROR FRAME RECEIVED***")
            # print("{id:0>8b}  {dlc}  {data}  {timestamp}".format(
            #     id=frame.id,
            #     dlc=frame.dlc,
            #     data=' '.join('%02x' % i for i in frame.data),
            #     timestamp=frame.timestamp
            # ))
            pass
        else:
            print("{id:0>8b}  {dlc}  {data}  {timestamp}".format(
                id=frame.id,
                dlc=frame.dlc,
                data=' '.join('%02x' % i for i in frame.data),
                timestamp=frame.timestamp
            ))
            
    except(canlib.canNoMsg) as ex:
         None
    except (canlib.canError) as ex:
        print(ex)
        finished = True

#******* End Add by HZC *******#

# print("Sending a message")
# frame = Frame(id_=123,
#               data=[1, 2, 3, 4, 5, 6, 7, 8],
#               dlc=8,
#               flags=0)
# ch.write(frame)
print("Going off bus")
ch.busOff()

print("Closing channel")
ch.close()
