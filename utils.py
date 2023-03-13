class exchange():
    def __new__(self, clf, timeout_s):
        def e(data):
            if data is None:
                return clf.exchange(None, timeout_s)[1:]
            else:
                return clf.exchange((len(data)+1).to_bytes(1, "big") + data, timeout_s)[1:]
        return e


FORMAT_VERSION = '0.4'
