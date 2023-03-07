import nfc
from nfc.clf import RemoteTarget, TimeoutError
import sys
from exchange import exchange
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

            if r[0] == 0x01:  # polling
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
    device = args.device
    timeout_s = args.timeout
    system_code = args.system_code

    clf = nfc.ContactlessFrontend(device)
    try:
        target = clf.sense(RemoteTarget("212F"))
        if target is None:
            print('No card', file=sys.stderr)
            exit(1)

        command(exchange(clf, timeout_s), system_code)
    finally:
        clf.close()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Communicate directly with FeliCa')

    parser.add_argument('--device', default='usb',
                        help='specify device (DEFAULT:usb)')
    parser.add_argument('-t', '--timeout', type=float, default=1.,
                        help='exchange timeout [s] (DEFAULT:1s)')
    parser.add_argument('-s', '--system-code', default='FFFF',
                        help='polling system code (DEFAULT:FFFF)')

    args = parser.parse_args()

    main(args)
