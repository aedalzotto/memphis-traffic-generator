from .descriptor import Descriptor

class Testcase(Descriptor):
    def __init__(self, slots, ht=False):
        super().__init__()
        self._content += "hw:\n"
        self._content += "  page_size_inst_KB: 64\n"
        self._content += "  page_size_data_KB: 64\n"
        self._content += "  tasks_per_PE: 1\n"
        self._content += "  mpsoc_dimension: [{},{}]\n".format(slots.x, slots.y)
        self._content += "  Peripherals:\n"
        self._content += "    - name: APP_INJ\n"
        self._content += "      pe: {},0\n".format(slots.x - 1)
        self._content += "      port: S\n"
        self._content += "    - name: MA_INJ\n"
        self._content += "      pe: 0,{}\n".format(slots.y - 1)
        self._content += "      port: N\n"
        if ht:
            self._content += "  links:\n"
            for ix in range(slots.x):
                for iy in range(slots.y):
                    for ip in ['E', 'W', 'N', 'S']:
                        if ix == 0 and ip == 'W':
                            continue
                        if ix == slots.x - 1 and ip == 'E':
                            continue
                        if iy == 0 and ip == 'S':
                            continue
                        if iy == slots.y - 1 and ip == 'N':
                            continue
                        self._content += "    - pe: [{},{}]\n".format(ix, iy)
                        self._content += "      port: {}\n".format(ip)
                        self._content += "      trojan: rs\n"
        self._content += "  parameters:\n"
        # self._content += "    - TRAFFIC_DEBUG: no\n"
        # self._content += "    - UART_DEBUG: no\n"
        # self._content += "    - SCHED_DEBUG: no\n"
        # self._content += "    - PIPE_DEBUG: no\n"
        self._content += "    - DMNI_DEBUG: yes\n"
