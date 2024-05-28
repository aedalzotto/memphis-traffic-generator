class Descriptor:
    def __init__(self):
        self._content = ""

    def write(self, path):
        with open(path, 'w') as f:
            f.write(self._content)
