from .descriptor import Descriptor

class Testcase(Descriptor):
    def __init__(self, x, y, mal=False):
        super().__init__()
        self._content += "hw:\n"
        self._content += "  page_size_inst_KB: 64\n"
        self._content += "  page_size_data_KB: 64\n"
        self._content += "  tasks_per_PE: 1\n"
        self._content += "  mpsoc_dimension: [{},{}]\n".format(x, y)
        self._content += "  Peripherals:\n"
        self._content += "    - name: APP_INJ\n"
        self._content += "      pe: {},0\n".format(x - 1)
        self._content += "      port: S\n"
        self._content += "    - name: MA_INJ\n"
        self._content += "      pe: 0,{}\n".format(y - 1)
        self._content += "      port: N\n"
        if mal:
            self._content += "  links:\n"
            for ix in range(x):
                for iy in range(y):
                    if ix == 0 and iy == y - 1:
                        continue
                    for ip in ['E', 'W', 'N', 'S']:
                        if ix == 0 and ip == 'W':
                            continue
                        if ix == x - 1 and ip == 'E':
                            continue
                        if iy == 0 and ip == 'S':
                            continue
                        if iy == y - 1 and ip == 'N':
                            continue
                        self._content += "    - pe: [{},{}]\n".format(ix, iy)
                        self._content += "      port: {}\n".format(ip)
                        self._content += "      trojan: rs\n"
        self._content += "  parameters:\n"
        self._content += "    - DMNI_DEBUG: yes\n"
