import nfc
from nfc.clf import RemoteTarget
from utils import exchange
fromhex = bytearray.fromhex


def dump(exchange, idm_byte):
    card = {'version': '0.1'}

    # Request System Code
    response_RSC = exchange(fromhex(f'0C {idm_byte.hex()}'))
    system_codes = [response_RSC[10:][i*2:(i+1)*2].hex()
                    for i in range(response_RSC[9])]

    for system_code in system_codes:
        system = dict()

        # Polling
        idm = exchange(fromhex(f'00 {system_code} 00 00'))[1:9].hex()

        system['IDm'] = idm

        service_codes = []

        for i in range(0xFFFF):
            # Search Service Code
            command_SSC = fromhex(f'0A {idm}') + i.to_bytes(2, "little")
            response_SSC = exchange(command_SSC)

            s = response_SSC[9:].hex()
            if s == 'ffff':
                break

            service_codes.append(s)

        for service_code in service_codes:
            service = dict()
            if len(service_code)//2 == 2:
                # Request Service
                command_RS = fromhex(f'02 {idm} 01 {service_code}')
                response_RS = exchange(command_RS).hex()

                if response_RS.endswith('0000'):
                    block = 0x8000
                    while True:
                        # Read Without Encryption
                        command_RWE = fromhex(f'06 {idm} 01 {service_code} 01') + \
                            block.to_bytes(2, "big")
                        response_RWE = exchange(command_RWE)
                        SF1, SF2 = response_RWE[9], response_RWE[10]
                        if SF1 != 0x00:
                            break
                        data = response_RWE[12:].hex()
                        service['%04x' % (block)] = data
                        block += 1

            if len(service) != 0:
                system[service_code] = service

        card[system_code] = system

    return card


def main(args):
    import json

    device = 'usb'

    clf = nfc.ContactlessFrontend(device)

    try:
        target = clf.sense(RemoteTarget("212F"))
        assert target is not None, 'No card'
        idm = target.sensf_res[1:9]
        pmm = target.sensf_res[9:17]
        card = dump(exchange(clf, 1.), idm)
        card['PMm'] = pmm.hex()
        print(json.dumps(card, indent=True))
    finally:
        clf.close()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    # parser.add_argument()

    args = parser.parse_args()

    main(args)
