from os import listdir
from .descriptor import Descriptor

class Application(Descriptor):
    def __init__(self, path, name, mal_msg_size):
        self._name = name
        self._mal_msg_size = mal_msg_size

        self.tasks = []
        for file in listdir("{}/applications/{}".format(path, name)):
            if file.endswith(".c"):
                task = file.split(".")[0]
                self.tasks.append(task)

        super().__init__()
        self._content += "apps:\n"
        self._content += "  - name: {}\n".format(name)
        self._content += "  - name: malicious_rand\n"
        self._content += "    instance: std_{}\n".format(mal_msg_size)
        self._content += "    definitions:\n"
        self._content += "      - MAL_MSG_SIZE: {}\n".format(mal_msg_size)

    @property
    def name(self):
        return self._name
    
    @property
    def mal_msg_size(self):
        return self._mal_msg_size

    def __len__(self):
        return len(self.tasks)
