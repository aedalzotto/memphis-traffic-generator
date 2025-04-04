from .descriptor import Descriptor

class Scenario(Descriptor):
    def __init__(self, app, mapping, management, ht=False):
        super().__init__()
        self._content     += "management:\n"
        for oda in management:
            self._content     += "  - task: {}\n".format(oda[0])
            self._content     += "    static_mapping: [{}, {}]\n".format(oda[1][0], oda[1][1])
    
        links = "links:\n"

        self._content     += "apps:\n"
        self._content     += "  - name: {}\n".format(app.name)
        self._content     += "    static_mapping:\n"
        for i, task in enumerate(app.tasks):
            self._content += "      {}: [{},{}]\n".format(task, mapping[i][0], mapping[i][1])
            for p in ['E', 'W', 'N', 'S']:
                links += "  - pe: [{},{}]\n".format(mapping[i][0], mapping[i][1])
                links += "    port: {}\n".format(p)
                links += "    trojan: rs\n"
                links += "    parameters:\n"
                links += "      tick_begin: 0\n"
                links += "      filter_app: 1\n"
                links += "      filter_prod: {}\n".format(i)

        if ht:
            self._content += links
