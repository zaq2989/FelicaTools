import nfc
from nfc.clf import LocalTarget, TimeoutError, BrokenLinkError
import sys
fromhex = bytearray.fromhex


def emulate(clf, card,  system_code, TIMEOUT=1.):
    sensf_res = fromhex('01'+card[system_code]['idm']+card['pmm']+system_code)

    print('waiting reader...', file=sys.stderr)
    target = None
    while target is None:
        target = clf.listen(LocalTarget(
            "212F", sensf_res=sensf_res), timeout=1.)

    tt3_cmd = target.tt3_cmd
    command = (len(tt3_cmd) + 1).to_bytes(1, "big") + tt3_cmd

    while True:
        print('<<', command.hex())
        command_code = command[1]
        response = None
        if command_code == 0x00:  # Polling
            pass  # TODO
        if command_code == 0x04:  # Request Response
            idm = command[2:10]
            response = f'05{idm}00'
            # TODO
        if command_code == 0x06:  # Read Without Encryption
            m = command[11]
            # TODO
        if command_code == 0x0A:  # Request System Code
            pass  # TODO
        if command_code == 0x0C:  # Request System Code
            pass  # TODO

        if response is None:  # TODO
            print('', file=sys.stderr)  # TODO
            continue

        assert isinstance(response, bytearray)
        print('>>', response.hex())
        try:
            command = clf.exchange(response, TIMEOUT)
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
    DEVICE = 'usb:054c:06c3'
    # DEVICE = args.device
    TIMEOUT = args.timeout

    system_code = 'FE00'.lower()

    card = json.loads(open(FILE, 'r').read().lower())

    # if card['idm'] == 'random':  # TODO
    #     import random
    #     pass

    clf = nfc.ContactlessFrontend(DEVICE)

    try:
        emulate(clf, card, system_code)
    finally:
        clf.close()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Emulate FeliCa Card')

    parser.add_argument('FILE', help='RePlay File')
    parser.add_argument('-t', '--timeout', type=float)
    parser.add_argument('--device')

    args = parser.parse_args()

    main(args)
