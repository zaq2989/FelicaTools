import nfc
from nfc.clf import RemoteTarget, TimeoutError
import argparse
import sys
fromhex = bytearray.fromhex


def main(args):
    device = args.device
    human_mode = not args.machine_mode
    TIMEOUT = args.timeout
    system_code = args.system_code
    assert len(system_code) == 4

    clf = nfc.ContactlessFrontend(device)

    target = RemoteTarget("212F")
    sensf_req = fromhex(f'00{system_code}0100')
    target.sensf_req = sensf_req
    if human_mode:
        print('<< #', sensf_req.hex())
    target = clf.sense(target)
    if target is None:
        print('No card', file=sys.stderr)
        exit(1)

    sensf_res = target.sensf_res
    if human_mode:
        idm = sensf_res[1:9].hex()
        print('>> #', sensf_res.hex())

    while True:
        try:
            if human_mode:
                i = input('<< # ')
            else:
                i = input('<< ')
            if human_mode:
                i = i.replace(' ', '')
                if i == '':
                    continue
                i = i.lower().replace('[idm]', idm)
                i = ('%02x' % (len(i)//2+1)) + i

            r = clf.exchange(fromhex(i), TIMEOUT)

            if human_mode:
                if r[1] == 0x01:  # polling
                    idm = r[2:10].hex()
            h = r.hex()
            if human_mode:
                assert r[0] == len(r)
                h = '# ' + h[2:]
                h = h.replace(idm, ' [IDm] ')
            print('>>', h)
        except KeyboardInterrupt:
            break
        except EOFError:
            break
        except ValueError as e:
            if human_mode:
                print(e, file=sys.stderr)
            else:
                break
        except TimeoutError:
            if human_mode:
                print('TIMEOUT', file=sys.stderr)
            else:
                continue  # explicitly

    clf.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Communicate directly with FeliCa')

    parser.add_argument('--device', default='usb',
                        help='specify device (DEFAULT:usb)')
    parser.add_argument('-m', '--machine-mode', action='store_true',
                        help='turn into machine mode')
    parser.add_argument('-t', '--timeout', type=float, default=1.,
                        help='exchange timeout [s] (DEFAULT:1s)')
    parser.add_argument('-s', '--system-code', default='FFFF',
                        help='sensing system code (DEFAULT:FFFF)')

    args = parser.parse_args()

    main(args)
