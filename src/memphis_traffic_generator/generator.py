from os import makedirs
from itertools import permutations
from tqdm import tqdm
from .application import Application
from .slots import Slots
from .testcase import Testcase
from .scenario import Scenario

class Generator:
    def __init__(self, platform_path, app, trojan=False, oda=False, mal_msg_size=None):
        self._trojan = trojan
        self.app = Application(platform_path, app, trojan, mal_msg_size)

        overhead = (1 if trojan else 3) + (2 if oda else 0)
        slots = Slots(len(self.app) + overhead)

        management = [(slots.x-1, slots.y-1)]
        if oda:
            # map the observing task at center
            obs_map = (int(slots.x / 2), int(slots.y / 2))
            
            # map the decision task right next to observing
            if obs_map[1] + 1 < slots.y:
                dec_map = (obs_map[0], obs_map[1] + 1)
            elif obs_map[1] - 1 >= 0:
                dec_map = (obs_map[0], obs_map[1] - 1)
            elif obs_map[0] + 1 < slots.x:
                dec_map = (obs_map[0] + 1, obs_map[1])
            else:
                dec_map = (obs_map[0] - 1, obs_map[1])

            management.append(obs_map)
            management.append(dec_map)

        if not trojan:
            self.tc  = Testcase(slots)
        else:
            self.tc  = (
                Testcase(slots), 
                Testcase(slots, management, mal=True)
            )

        slots.remove(management)
        mappings = [tuple(slots.to_xy(i) for i in m) for m in list(permutations(slots, len(self.app)))]

        if not trojan:
            self.scenarios = [
                (
                    Scenario(self.app, p, management, slots), 
                    Scenario(self.app, p, management, slots, mal_msg_size)
                ) 
                for p in mappings
            ]
        else:
            self.scenarios = [
                Scenario(self.app, p, management, slots)
                for p in mappings
            ]

    def write(self, out_path):
        makedirs(out_path, exist_ok=True)
        print("Generating testcase...")
        if not self._trojan:
            self.tc.write("{}/tc_{}_{}.yaml".format(out_path, self.app.name, self.app.mal_msg_size))
        else:
            self.tc[0].write("{}/tc_{}.yaml".format(out_path, self.app.name))
            self.tc[1].write("{}/tc_{}_m.yaml".format(out_path, self.app.name))
        
        print("Generating application...")
        if not self._trojan:
            self.app.write("{}/applications_{}_{}.yaml".format(out_path, self.app.name, self.app.mal_msg_size))
        else:
            self.app.write("{}/applications_{}.yaml".format(out_path, self.app.name))

        # Not worth parallelizing scenarios. Already tried that.
        print("Generating scenarios...")
        if not self._trojan:
            makedirs("{}/{}_{}".format(out_path, self.app.name, self.app.mal_msg_size), exist_ok=True)
            for i, pair in enumerate(tqdm(self.scenarios)):
                self.__write_scenario(i, pair, out_path)
        else:
            makedirs("{}/{}".format(out_path, self.app.name), exist_ok=True)
            for i, scenario in enumerate(tqdm(self.scenarios)):
                scenario.write("{}/{}/sc_{}.yaml".format(out_path, self.app.name, i))

    def __write_scenario(self, i, pair, out_path):
        pair[0].write("{}/{}_{}/sc_{}.yaml".format(out_path, self.app.name, self.app.mal_msg_size, i))
        pair[1].write("{}/{}_{}/sc_{}_m.yaml".format(out_path, self.app.name, self.app.mal_msg_size, i))
