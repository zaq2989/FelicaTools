#!/usr/bin/env python3

import nfc
from nfc.clf import RemoteTarget, TimeoutError
import sys
from base import *
fromhex = bytearray.fromhex


def command(exchange, system_code):
    assert len(system_code) == 4
    idm = ''
    while True:
        try:
            print('<< # ', end='')
            if idm == '':
                i = f'00 {system_code} 00 00'
                print(i)
            else:
                i = input()
            i = i.replace(' ', '')
            if i == '':
                continue
            i = i.lower().replace('[idm]', idm)

            r = exchange(fromhex(i))

            if r[0] == 0x01:  # Polling
                idm = r[1:9].hex()
                print(f'\t[IDm] set to {idm}', file=sys.stderr)
            h = r.hex()
            h = '# ' + h
            h = h.replace(idm, ' [IDm] ')
            print('>>', h)
        except (KeyboardInterrupt, EOFError):
            break
        except ValueError as e:
            print(e, file=sys.stderr)
        except TimeoutError:
            print('TIMEOUT', file=sys.stderr)


def main(args):
    system_code = args.system_code
    timeout_s = args.timeout
    device = args.device

    try:
        clf = nfc.ContactlessFrontend(device)
    except OSError:
        print('No device', file=sys.stderr)
        exit(3)

    try:
        target = clf.sense(RemoteTarget("212F"))
        if target is None:
            print('No card', file=sys.stderr)
            exit(1)

        command(make_exchange(clf, timeout_s), system_code)
    finally:
        clf.close()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Communicate directly with FeliCa')

    parser.add_argument('-s', '--system-code', metavar='', default='FFFF',
                        help=f'polling system code {HELP_DEFAULT}')
    add_base_argument(parser)

    args = parser.parse_args()

    main(args)
