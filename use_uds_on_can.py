# import SomeLib.SomeCar.SomeModel as MyCar

import udsoncan
from udsoncan.connections import IsoTPSocketConnection,BaseConnection
from udsoncan.client import Client
from udsoncan.exceptions import *
from udsoncan.services import *

from canlib import canlib, Frame

import flask_project_use_socket.app.controllers.can_message as can


class MyConnection(BaseConnection):
    def __init__(self,rxid,txid,ch,name = None):
        BaseConnection.__init__(self, name)
        self.ch = ch
    
    def open(self):
        self.ch = can.init()
        self.ch = can.run(ch)
        # return ch

    def close(self):
        self.ch.busOff()
        self.ch.close()

    def specific_send(self,frame):
        self.ch.write(frame)

    def specific_wait_frame(self,timeout = 2):
        pass

    def empty_rxqueue(self):
        pass

# 定义自己车的常量和方法
class MyCar:
    config = {"exception_on_negative_response":True,
    "exception_on_invalid_respons":True,
    "exception_on_unexpected_response":True,
    "security_algo":SomeAlgorithm}

    def __init__(self):
        pass
    
    def SomeAlgorithm(self,level,seed,params):
        pass
    pass
    

udsoncan.setup_logging()

# conn = IsoTPSocketConnection('can0', rxid=0x123, txid=0x456)
ch = None
conn = MyConnection(rxid=0x79D, txid=0x888,ch=ch)
MyCar = MyCar()
# with Client(conn,  request_timeout=2, config=MyCar.config) as client:
with Client(conn,  request_timeout=2,config=MyCar.config) as client:
    pass
#     try:
#         client.change_session(DiagnosticSessionControl.Session.extendedDiagnosticSession)  # integer with value of 3
#         # client.unlock_security_access(MyCar.debug_level)   # Fictive security level. Integer coming from fictive lib, let's say its value is 5
#         # client.write_data_by_identifier(udsoncan.DataIdentifier.VIN, 'ABC123456789')       # Standard ID for VIN is 0xF190. Codec is set in the client configuration
#         print('Vehicle Identification Number successfully changed.')
#         # client.ecu_reset(ECUReset.ResetType.hardReset)  # HardReset = 0x01
#     except NegativeResponseException as e:
#         print('Server refused our request for service %s with code "%s" (0x%02x)' % (e.response.service.get_name(), e.response.code_name, e.response.code))
#     except InvalidResponseException as e:
#         print('Server sent an invalid payload : %s' % e.response.original_payload)
#     except  UnexpectedResponseException as e:
#         print('Server sent an invalid payload : %s' % e.response.original_payload)