from os import listdir
from .descriptor import Descriptor

class Application(Descriptor):
    def __init__(self, path, name):
        self._name = name

        self.tasks = []
        for file in listdir("{}/applications/{}".format(path, name)):
            if file.endswith(".c"):
                task = file.split(".")[0]
                self.tasks.append(task)

        super().__init__()
        self._content += "apps:\n"
        self._content += "  - name: {}\n".format(name)

    @property
    def name(self):
        return self._name

    def __len__(self):
        return len(self.tasks)
