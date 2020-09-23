from usb_can_analyzer import Converter

converter = Converter(port="COM4",baudrate=9600)

while True:
    try:
        data = converter.readMessage()
    except ValueError as e:
        print(e)
    # data = converter.readMessage()
    print(data)