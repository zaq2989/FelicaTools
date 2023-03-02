import nfc
from nfc.clf import RemoteTarget, LocalTarget, TimeoutError, BrokenLinkError
fromhex = bytearray.fromhex

#TODO IDm memory


def search_device():
    for b in range(1, 10):
        for d in range(50):
            device = f'usb:{b:03d}:{d:03d}'
            try:
                nfc.ContactlessFrontend(device)
                return device
            except OSError:
                pass


def main():
    TIMEOUT = 1
    device = search_device()
    clf = nfc.ContactlessFrontend(device)
    target = clf.sense(RemoteTarget("212F"))

    while True:
        r = clf.exchange(fromhex(input()), TIMEOUT)
        print(r.hex())


if __name__ == '__main__':
    main()
