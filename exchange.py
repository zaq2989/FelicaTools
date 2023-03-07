class exchange():
    def __new__(self, clf, timeout_s):
        return lambda command: clf.exchange((len(command)+1).to_bytes(1, "big") + command, timeout_s)[1:]
