import nfc
from nfc.clf import RemoteTarget


def exchange(clf, command, timeout):
    command = (len(command)+1).to_bytes(1, "big") + command

    response = clf.exchange(command, timeout)

    return response


def dump(clf):
    target = RemoteTarget("212F")
    sensf_req = bytearray.fromhex(f'00 FE00 01 00')
    target.sensf_req = sensf_req
    target = clf.sense(target)

    assert target is not None

    idm = target.sensf_res[1:9]

    response = exchange(clf, b'\x0C' + idm, 1.)
    print(response.hex())

    system_codes = response[11:]

    service_codes = []

    for i in range(0xFFFF):
        command = b'\x0A'+idm+i.to_bytes(2, "little")
        response = exchange(clf, command, 1.)

        s = response[10:]
        if s == b'\xFF\xFF':
            break

        service_codes.append(s)

    for s in service_codes:
        print(s.hex())


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
