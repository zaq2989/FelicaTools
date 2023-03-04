import nfc
from nfc.clf import RemoteTarget


def prependLEN(data):
    return (len(data)+1).to_bytes(1, "big")+data


def dump(clf):
    target = RemoteTarget("212F")
    sensf_req = bytearray.fromhex(f'00 FE00 01 00')
    target.sensf_req = sensf_req
    target = clf.sense(target)

    assert target is not None

    idm = target.sensf_res[1:9]

    response = clf.exchange(prependLEN(b'\x0C' + idm), 1.)
    print(f'{response.hex()=}')

    system_codes = response[11:]

    service_codes = []

    for i in range(0xFFFF):
        command = b'\x0A'+idm+i.to_bytes(2, "little")
        response = clf.exchange(prependLEN(command), 1.)

        s = response[10:]
        if s == b'\xFF\xFF':
            break

        service_codes.append(s)

    for s in service_codes:
        print(f'{s.hex()=}')
        if len(s) == 2:
            command = b'\x02' + idm + b'\x01' + s
            response = clf.exchange(prependLEN(command), 1.)
            print(f'{response.hex()=}')

            if response.endswith(b'\x00\x00'):

                command2 = b'\x06' + idm + b'\x01'+s+b'\x01'+b'\x80\x00'
                response2 = clf.exchange(prependLEN(command2), 1.)
                print(f'{response2.hex()=}')


def main(args):
    device = 'usb'

    clf = nfc.ContactlessFrontend(device)

    dump(clf)

    clf.close()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    # parser.add_argument()

    args = parser.parse_args()

    main(args)
