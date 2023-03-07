import nfc
from nfc.clf import LocalTarget, TimeoutError, BrokenLinkError
import sys
from utils import *
fromhex = bytearray.fromhex


def emulate(exchange, card, system_code, command):
    while True:
        idm = card[system_code]['idm']
        print('<< #', command.hex())
        command_code = command[0]
        response = None
        if command_code == 0x00:  # Polling
            s = command[1:3].hex()
            request_code = command[3]
            if s in card:
                system_code = s
                response = fromhex(
                    f'01 {card[system_code]["idm"]} {card["pmm"]}')
                if request_code == 0x01:
                    response += fromhex(system_code)
                if request_code == 0x02:
                    response += fromhex('0083')
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
            system_codes = [s for s in card.keys() if len(s) == 4]
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
    # timeout_s = args.timeout
    timeout_s = 1.

    system_code = 'FE00'.lower()

    card = json.loads(open(FILE, 'r').read().lower())

    assert card['version'] == VERSION, 'unsupported version'

    if card[system_code]['idm'] == 'random':
        import random
        card[system_code]['idm'] = random.randbytes(8).hex()

    clf = nfc.ContactlessFrontend(device)

    try:
        sensf_res = fromhex(
            '01' + card[system_code]['idm'] + card['pmm'] + system_code)

        print('waiting reader...', file=sys.stderr)

        target = None
        while target is None:
            target = clf.listen(LocalTarget(
                "212F", sensf_res=sensf_res), timeout=1.)

        emulate(exchange(clf, timeout_s), card,
                system_code, target.tt3_cmd)
    finally:
        clf.close()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Emulate FeliCa Card')

    parser.add_argument('FILE', help='FeliCa File')
    parser.add_argument('-t', '--timeout', type=float)
    parser.add_argument('--device')

    args = parser.parse_args()

    main(args)
