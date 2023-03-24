FORMAT_VERSION = '0.5'
HELP_DEFAULT = '(default:%(default)s)'


def add_base_argument(parser):
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-t', '--timeout', metavar='', type=float, default=1.,
                        help=f'exchange timeout [s] {HELP_DEFAULT}')
    parser.add_argument('--device', metavar='PATH', default='usb',
                        help=f'local device search path {HELP_DEFAULT}')


def make_exchange(clf, timeout_s):
    def exchange(data):
        if data is None:
            payload = None
        else:
            payload = (len(data)+1).to_bytes(1, "big") + data
        return clf.exchange(payload, timeout_s)[1:]

    return exchange
