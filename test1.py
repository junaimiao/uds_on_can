import udsoncan
from udsoncan.connections import IsoTPSocketConnection
from udsoncan.client import Client
from udsoncan.exceptions import *
from udsoncan.services import *

udsoncan.setup_logging()

conn = IsoTPSocketConnection('can0', rxid=0x79D, txid=0x79D)
with Client(conn,  request_timeout=2) as client:
    try:
        client.change_session(DiagnosticSessionControl.Session.extendedDiagnosticSession)  # integer with value of 3
        # client.unlock_security_access(MyCar.debug_level)   # Fictive security level. Integer coming from fictive lib, let's say its value is 5
        client.write_data_by_identifier(udsoncan.DataIdentifier.VIN, 'ABC123456789')       # Standard ID for VIN is 0xF190. Codec is set in the client configuration
        print('Vehicle Identification Number successfully changed.')
        client.ecu_reset(ECUReset.ResetType.hardReset)  # HardReset = 0x01
    except NegativeResponseException as e:
      print('Server refused our request for service %s with code "%s" (0x%02x)' % (e.response.service.get_name(), e.response.code_name, e.response.code))
#    except InvalidResponseException , UnexpectedResponseException as e:
    except InvalidResponseException as e:
        print('Server sent an invalid payload : %s' % e.response.original_payload)
    except UnexpectedResponseException as e:
        print('Server sent an invalid payload : %s' % e.response.original_payload)