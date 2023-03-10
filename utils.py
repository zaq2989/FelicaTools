class exchange():
    def __new__(self, clf, timeout_s):
        return lambda data: clf.exchange((len(data)+1).to_bytes(1, "big") + data, timeout_s)[1:]


VERSION = '0.3'
