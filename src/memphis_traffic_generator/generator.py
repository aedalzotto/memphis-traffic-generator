from math import sqrt, ceil
from os import makedirs
from itertools import permutations
from tqdm import tqdm
from .application import Application
from .slots import Slots
from .testcase import Testcase
from .scenario import Scenario

class Generator:
    def __init__(self, platform_path, app, trojan=False, mal_msg_size=None):
        self._trojan = trojan
        self.app = Application(platform_path, app, trojan, mal_msg_size)

        fit = Generator.__fit(len(self.app), trojan)

        if not trojan:
            self.tc  = Testcase(fit.x, fit.y)
        else:
            self.tc  = (
                Testcase(fit.x, fit.y), 
                Testcase(fit.x, fit.y, mal=True)
            )

        if not trojan:
            self.scenarios = [
                (
                    Scenario(self.app, mal_msg_size, p, fit.x, fit.y), 
                    Scenario(self.app, mal_msg_size, p, fit.x, fit.y, mal=True)
                ) 
                for p in list(permutations(fit, len(self.app)))
            ]
        else:
            self.scenarios = [
                Scenario(self.app, mal_msg_size, p, fit.x, fit.y)
                for p in list(permutations(fit, len(self.app))) 
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

    def __fit(app_size, trojan):
        overhead = 1 if trojan else 3

        mc_size = ceil(sqrt(app_size + overhead))
        fits = []

        # Possible fit: mc_size*mc_size (square)
        fits.append(Slots(mc_size, mc_size, ht=trojan))

        # Possible fit: rectangular
        if (mc_size*(mc_size-1) - overhead) >= app_size:
            fits.append(Slots(mc_size, mc_size-1, ht=trojan))
            
        # Possible fit: half the square size
        if (mc_size*(mc_size + 1)/2 - (overhead-1)) >= app_size:
            fits.append(Slots(mc_size, mc_size, rem_top_diag=True, ht=trojan))

        # Possible fit: half of the bigger square
        if ((mc_size + 1)*(mc_size + 2)/2 - (overhead-1)) >= app_size:
            fits.append(Slots(mc_size+1, mc_size+1, rem_top_diag=True, ht=trojan))
        
        return sorted(fits)[0]
