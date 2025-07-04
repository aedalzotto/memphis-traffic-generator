from os import makedirs
from itertools import permutations
from tqdm import tqdm
from .application import Application
from .slots import Slots
from .testcase import Testcase
from .scenario import Scenario
from random import sample, seed

class Generator:
    def __init__(self, platform_path, app, proportion, rtd, mc_size=None, fp_rtd=False):
        self.app = Application(platform_path, app)

        overhead = (3 if (rtd or fp_rtd) else 1)
        if mc_size is None:
            self.slots = Slots(len(self.app) + overhead)
        else:
            self.slots = Slots(int(mc_size[0]) * int(mc_size[1]))

        self.tc = Testcase(self.slots, ht=True)

        management = [("mapper_task", (self.slots.x-1, self.slots.y-1))]
        if rtd or fp_rtd:
            # map the observing task at center
            obs_map = (int(self.slots.x / 2), int(self.slots.y / 2))
            # @todo check if colliding with mapper_task (unlikely)
            
            # map the decision task right next to observing
            if obs_map[0] + 1 < self.slots.x and not (obs_map[0]+1 == self.slots.x-1 and obs_map[1] == self.slots.y-1):
                dec_map = (obs_map[0] + 1, obs_map[1])
            elif obs_map[1] + 1 < self.slots.y and not (obs_map[0] == self.slots.x-1 and obs_map[1]+1 == self.slots.y-1):
                dec_map = (obs_map[0], obs_map[1] + 1)
            elif obs_map[1] - 1 >= 0:
                dec_map = (obs_map[0], obs_map[1] - 1)
            else:
                dec_map = (obs_map[0] - 1, obs_map[1])

            management.append(("safe-monitor", obs_map))
            management.append(("safe-{}{}".format(app, "_fp" if fp_rtd else ""), dec_map))

        for oda in management:
            self.slots.remove(oda[1])
        mappings = [tuple(self.slots.to_xy(i) for i in m) for m in list(permutations(self.slots, len(self.app)))]

        train_len = int(len(mappings)*proportion)
        self.proportion = proportion

        seed(7)
        train_mappings = sample(mappings, train_len)
        test_mappings  = list(set(mappings) - set(train_mappings))

        self.train_scenarios = [
            Scenario(self.app, p, [management[0]])
            for p in train_mappings
        ]

        self.test_scenarios = [
            Scenario(self.app, p, [management[0]], ht=True)
            for p in test_mappings
        ]

        if rtd or fp_rtd:
            self.rtd_scenarios = [
                Scenario(self.app, p, management, ht=True)
                for p in test_mappings
            ]
        else:
            self.rtd_scenarios = None

    def write(self, out_path):
        makedirs(out_path, exist_ok=True)
        print("Generating testcase...")
        tc_name = "tc_{}_{}x{}.yaml".format(self.app.name, self.slots.x, self.slots.y)
        self.tc.write("{}/{}".format(out_path, tc_name))

        print("Generating application...")    
        app_name = "applications_{}.yaml".format(self.app.name)
        self.app.write("{}/{}".format(out_path, app_name))

        # Not worth parallelizing scenarios. Already tried that.
        scen_name = "{}_p{}".format(self.app.name, self.proportion)
        print("Generating training scenarios...")
        makedirs("{}/{}".format(out_path, scen_name), exist_ok=True)
        for i, scenario in enumerate(tqdm(self.train_scenarios)):
            scenario.write("{}/{}/sc_{}.yaml".format(out_path, scen_name, i))

        print("Generating testing scenarios...")
        for i, scenario in enumerate(tqdm(self.test_scenarios)):
            scenario.write("{}/{}/sc_{}_m.yaml".format(out_path, scen_name, i+len(self.train_scenarios)))

        if self.rtd_scenarios is not None:
            print("Generating RTD scenarios...")
            for i, scenario in enumerate(tqdm(self.rtd_scenarios)):
                scenario.write("{}/{}/sc_{}_rtd.yaml".format(out_path, scen_name, i+len(self.train_scenarios)))

        print("Output written to {}/{{{}, {}, {}}}".format(out_path, scen_name, tc_name, app_name))
