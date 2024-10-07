from .descriptor import Descriptor
from .slots import Slots

class Scenario(Descriptor):
    def __init__(self, app, mapping, management, slots, mal_msg_size=None):
        super().__init__()
        self._content     += "management:\n"
        for oda in management:
            self._content     += "  - task: {}\n".format(oda[0])
            self._content     += "    static_mapping: [{}, {}]\n".format(oda[1][0], oda[1][1])
    
        self._content     += "apps:\n"
        self._content     += "  - name: {}\n".format(app.name)
        self._content     += "    start_time_ms: 5\n"
        self._content     += "    static_mapping:\n"
        for i, task in enumerate(app.tasks):
            self._content += "      {}: [{},{}]\n".format(task, mapping[i][0], mapping[i][1])

        if mal_msg_size is not None:
            self._content += "  - name: malicious_rand\n"
            self._content += "    instance: std_{}\n".format(mal_msg_size)
            self._content += "    static_mapping:\n"
            self._content += "      producer: [{},{}]\n".format(0, 0)
            self._content += "      consumer: [{},{}]\n".format(slots.x-1, slots.y-1)
