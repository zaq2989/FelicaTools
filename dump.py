#!/usr/bin/env python3

import nfc
from nfc.clf import RemoteTarget, TimeoutError
import sys
from utils import *
fromhex = bytearray.fromhex


def dump(exchange, idm, system_code_filter, debug=False):
    def dprint(text):
        if debug:
            print(text, file=sys.stderr)

    card = {'version': VERSION}

    # Request System Code
    response_RSC = exchange(fromhex(f'0C {idm}'))
    system_codes = [response_RSC[10:][i*2:(i+1)*2].hex()
                    for i in range(response_RSC[9])]

    dprint(f'{system_codes=}')

    systems = {}

    for system_code in system_codes:
        if system_code_filter is not None:
            if system_code not in system_code_filter.split(',').lower():
                continue

        system = {}

        # Polling
        idm = exchange(fromhex(f'00 {system_code} 00 00'))[1:9].hex()

        system['IDm'] = idm

        service_code_candidates = []

        for i in range(0xFFFF):
            # Search Service Code
            command_SSC = fromhex(f'0A {idm}') + i.to_bytes(2, "little")
            response_SSC = exchange(command_SSC)

            s = response_SSC[9:].hex()
            if s == 'ffff':
                break

            if len(s)//2 == 2:
                service_code_candidates.append(s)
            if len(s)//2 == 4:
                service_code_candidates += [s[0:4], s[4:8]]

        dprint(f'{service_codes=}')

        services = {}

        for service_code in service_codes:
            service = {}
            if len(service_code)//2 == 2:
                # Request Service
                command_RS = fromhex(f'02 {idm} 01 {service_code}')
                response_RS = exchange(command_RS).hex()

                if not response_RS.endswith('ffff'):
                    blocks = {}
                    i = 0
                    while True:
                        # Read Without Encryption
                        command_RWE = fromhex(f'06 {idm} 01 {service_code} 01') + \
                            i.to_bytes(2, "big")
                        response_RWE = exchange(command_RWE)
                        SF1, SF2 = response_RWE[9], response_RWE[10]
                        if SF1 != 0x00:
                            break
                        data = response_RWE[12:].hex()
                        blocks['%04x' % block] = data
                        i += 1

                    if len(blocks) != 0:
                        service['version'] = response_RS[-4:]
                        service['blocks'] = blocks

            if len(service) != 0:
                services[service_code] = service

        if len(services) != 0:
            system['services'] = services

        systems[system_code] = system

    card['systems'] = systems

    return card


def main(args):
    import json

    device = args.device
    FILE = args.output
    system_code_filter = args.system_code_filter
    lite = args.lite
    debug = args.debug

    clf = nfc.ContactlessFrontend(device)

    try:
        target = clf.sense(RemoteTarget("212F"))
        if target is None:
            print('No card', file=sys.stderr)
            exit(1)

        sensf_res = target.sensf_res
        idm = sensf_res[1:9].hex()
        pmm = sensf_res[9:17].hex()
        if len(sensf_res) == 19:
            sc = sensf_res[17:19].hex()

        if sc == '88b4' and not lite:
            lite = True
            print('dumping FeliCa Lite is not supported', file=sys.stderr)
            print('fallback to lite mode', file=sys.stderr)

        if lite:
            card = {'version': VERSION, 'systems': {sc: {'IDm': idm}}}
        else:
            print('dumping...', file=sys.stderr)
            card = dump(exchange(clf, 1.), idm, system_code_filter, debug)
        card['PMm'] = pmm

        fc = json.dumps(card, indent=True)

        print()
        print(fc)
        print()

        if FILE is not None:
            open(FILE, 'w').write(fc)
            print(f'output to {FILE}', file=sys.stderr)
    except TimeoutError:
        print('TIMEOUT', file=sys.stderr)
    finally:
        clf.close()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--device', default='usb')
    parser.add_argument('-o', '--output', metavar='FILE')
    parser.add_argument('--system-code-filter')
    parser.add_argument('--lite', action='store_true')
    parser.add_argument('--debug', action='store_true')

    args = parser.parse_args()

    main(args)
