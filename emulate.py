#!/usr/bin/env python3

import nfc
from nfc.clf import LocalTarget, TimeoutError, BrokenLinkError
import sys
from utils import *
fromhex = bytearray.fromhex


def emulate(exchange, card, system_code, command, system_codes):
    while True:
        idm = card[system_code]['idm']
        print('<< #', command.hex())
        command_code = command[0]
        response = None
        if command_code == 0x00:  # Polling
            s = command[1:3].hex()
            request_code = command[3]
            if s in system_codes:
                system_code = s
                response = fromhex(
                    f'01 {card[system_code]["idm"]} {card["pmm"]}')
                if request_code == 0x01:
                    response += fromhex(system_code)
                if request_code == 0x02:
                    response += fromhex('0083')
            else:
                print('Unknown System Code', file=sys.stderr)
                print('Maybe scanning this?', file=sys.stderr)
                print(f"{sys.argv[0]} doesn't support being scanned",
                      file=sys.stderr)
                break
        if command_code == 0x04:  # Request Response
            response = fromhex(f'05 {idm} 00')
        if command_code == 0x06:  # Read Without Encryption
            m = command[9]
            assert m == 1, 'TODO'
            service_codes = [
                command[10+i*2:10+(i+1)*2].hex() for i in range(m)]
            n = command[10+m*2]
            assert n*2 == len(command)-(11+m*2), 'TODO'
            blocks = [command[11+m*2+i*2:11 +
                              m*2+(i+1)*2].hex() for i in range(n)]
            data = ''
            for block in blocks:
                data += card[system_code][service_codes[0]][block]
            response = fromhex(f'07 {idm} 00 00 {n:02x} {data}')
        if command_code == 0x0C:  # Request System Code
            response = fromhex(
                f'0D {idm} {len(system_codes):02x} {" ".join(system_codes)}')

        if response is None:
            print(f'Unknown command code: {command_code:02x}', file=sys.stderr)
            break

        assert isinstance(response, bytearray)
        print('>> #', response.hex())
        try:
            command = exchange(response)
        except KeyboardInterrupt:
            break
        except TimeoutError:
            print('TIMEOUT Reader', file=sys.stderr)
            break
        except BrokenLinkError:
            print('Exchange Finished', file=sys.stderr)
            break


def main(args):
    import json

    FILE = args.FILE
    device = 'usb:054c:06c3'
    # DEVICE = args.device
    timeout_s = args.timeout

    system_code = args.system_code

    card = json.loads(open(FILE, 'r').read().lower())

    # TODO 0.2
    assert card['version'] == '0.1', 'Unsupported version'

    system_codes = [s for s in card.keys() if len(s) == 4]

    if system_code is None:
        system_code = system_codes[0]
    else:
        if system_code not in system_codes:
            print(f'System Code "{system_code}" is not in the file',
                  file=sys.stderr)
            exit(1)

    if card[system_code]['idm'] == 'random':
        import random
        card[system_code]['idm'] = random.randbytes(8).hex()

    try:
        clf = nfc.ContactlessFrontend(device)
    except OSError:
        print('No device', file=sys.stderr)
        exit(1)

    try:
        sensf_res = fromhex(
            '01' + card[system_code]['idm'] + card['pmm'] + system_code)

        print('waiting reader...', file=sys.stderr)

        target = None
        while target is None:
            target = clf.listen(LocalTarget(
                "212F", sensf_res=sensf_res), timeout=1.)

        emulate(exchange(clf, timeout_s), card,
                system_code, target.tt3_cmd, system_codes)
    except KeyboardInterrupt:
        pass
    finally:
        clf.close()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Emulate FeliCa Card')

    parser.add_argument('FILE', help='FeliCa file')
    parser.add_argument('-t', '--timeout', type=float, default=1.)
    parser.add_argument('-s', '--system-code')
    parser.add_argument('--device')

    args = parser.parse_args()

    main(args)
