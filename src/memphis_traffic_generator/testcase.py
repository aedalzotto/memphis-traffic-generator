from .descriptor import Descriptor

class Testcase(Descriptor):
    def __init__(self, x, y):
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
        self._content += "  parameters:\n"
        self._content += "    - DMNI_DEBUG: yes\n"
