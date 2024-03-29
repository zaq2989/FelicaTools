#!/usr/bin/env python3

from nfc.clf import ContactlessFrontend, RemoteTarget, TimeoutError
import sys
from base import *
fromhex = bytearray.fromhex
from_bytes = int.from_bytes


def dump(raw_exchange, idm, system_codes_to_dump, debug=False):
    def dprint(*args):
        if debug:
            print(*args, file=sys.stderr)

    def exchange(command):
        dprint('<<', command.hex())
        response = raw_exchange(command)
        dprint('>>', response.hex())
        return response

    card = {'version': FORMAT_VERSION}

    # Request System Code
    response_RSC = exchange(fromhex(f'0C {idm}'))
    system_codes = [response_RSC[10:][i*2:(i+1)*2].hex()
                    for i in range(response_RSC[9])]

    dprint(f'{system_codes=}')

    systems = {}

    for system_code in system_codes:
        if system_codes_to_dump is not None:
            if system_code not in system_codes_to_dump:
                continue

        system = {}

        # Polling
        idm = exchange(fromhex(f'00 {system_code} 00 00'))[1:9].hex()

        system['IDm'] = idm

        service_codes = []

        for i in range(0xFFFF):
            # Search Service Code
            command_SSC = fromhex(f'0A {idm}') + i.to_bytes(2, "little")
            response_SSC = exchange(command_SSC)

            s = from_bytes(response_SSC[9:11], "little")
            if s == 0xFFFF:
                break

            service_codes.append(s)

        dprint(f'{service_codes=}')

        services = {}

        for service_code in service_codes:
            service = {}

            # Request Service
            command_RS = fromhex(f'02 {idm} 01') + \
                service_code.to_bytes(2, "little")
            response_RS = exchange(command_RS)
            key_version = from_bytes(response_RS[10:12], "little")
            dprint(f'{key_version=}')
            if service_code % 2 == 1:
                blocks = []
                i = 0
                while True:
                    # Read Without Encryption
                    command_RWE = fromhex(f'06 {idm} 01') + service_code.to_bytes(
                        2, "little") + fromhex('01 00') + i.to_bytes(2, "little")
                    response_RWE = exchange(command_RWE)
                    SF1, SF2 = response_RWE[9], response_RWE[10]
                    if SF1 != 0x00:
                        break
                    data = response_RWE[12:].hex()
                    blocks.append(data)
                    i += 1
                if len(blocks) != 0:
                    # service['key_version'] = key_version
                    service['blocks'] = blocks

            if len(service) != 0:
                services[service_code.to_bytes(2, "big").hex()] = service

        if len(services) != 0:
            system['services'] = services

        systems[system_code] = system

    card['systems'] = systems

    return card


def main(args):
    import json

    device = args.device
    FILE = args.output
    system_codes_to_dump = args.system_codes
    lite = args.lite
    debug = args.debug

    try:
        clf = ContactlessFrontend(device)
    except OSError:
        print('No device', file=sys.stderr)
        exit(3)

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
        else:
            sc = 'ffff'

        if lite:
            card = {'name': idm, 'systems': {sc: {'IDm': idm}}}
        else:
            print('dumping...', file=sys.stderr)
            card = dump(make_exchange(clf, 1.), idm,
                        system_codes_to_dump, debug)
        card['PMm'] = pmm

        fc = json.dumps(card, indent=2)

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

    parser = argparse.ArgumentParser('Dump FeliCa')

    add_base_argument(parser)

    parser.add_argument('-o', '--output', metavar='FILE',
                        help='file to output')
    parser.add_argument('--system-codes', nargs='+',
                        metavar='', help='system code(s) to dump')
    parser.add_argument('--lite', action='store_true',
                        help='enable lite mode')

    args = parser.parse_args()

    main(args)
