from .descriptor import Descriptor
from .slots import Slots

class Scenario(Descriptor):
    def __init__(self, app, mal_msg_size, mapping, x, y, mal=False):
        mapper = x * (y-1)
        super().__init__()
        self._content     += "management:\n"
        self._content     += "  - task: mapper_task\n"
        self._content     += "    static_mapping: [{}, {}]\n".format(Slots.to_x(mapper, x), Slots.to_y(mapper, x))
        self._content     += "apps:\n"
        self._content     += "  - name: {}\n".format(app.name)
        self._content     += "    start_time_ms: 5\n"
        self._content     += "    static_mapping:\n"
        for i, task in enumerate(app.tasks):
            self._content += "      {}: [{},{}]\n".format(task, Slots.to_x(mapping[i], x), Slots.to_y(mapping[i], x))

        if mal:
            self._content += "  - name: malicious_rand\n"
            self._content += "    instance: std_{}\n".format(mal_msg_size)
            self._content += "    static_mapping:\n"
            self._content += "      producer: [{},{}]\n".format(0, 0)
            self._content += "      consumer: [{},{}]\n".format(x-1, y-1)
