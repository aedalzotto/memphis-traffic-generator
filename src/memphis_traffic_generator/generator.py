from math import sqrt, ceil
from os import makedirs
from itertools import permutations
from tqdm import tqdm
from .application import Application
from .slots import Slots
from .testcase import Testcase
from .scenario import Scenario

class Generator:
    __TASK_OVERHEAD = 3

    def __init__(self, platform_path, app, mal_msg_size):
        self.app = Application(platform_path, app, mal_msg_size)

        fit = Generator.__fit(len(self.app))

        self.tc  = Testcase(fit.x, fit.y)

        self.scenarios = [
            (
                Scenario(self.app, mal_msg_size, p, fit.x, fit.y), 
                Scenario(self.app, mal_msg_size, p, fit.x, fit.y, mal=True)
            ) 
            for p in list(permutations(fit, len(self.app)))
        ]

    def write(self, out_path):
        makedirs(out_path, exist_ok=True)
        print("Generating testcase...")
        self.tc.write("{}/tc_{}_{}.yaml".format(out_path, self.app.name, self.app.mal_msg_size))
        print("Generating application...")
        self.app.write("{}/applications_{}_{}.yaml".format(out_path, self.app.name, self.app.mal_msg_size))

        # Not worth parallelizing scenarios. Already tried that.
        makedirs("{}/{}_{}".format(out_path, self.app.name, self.app.mal_msg_size), exist_ok=True)
        print("Generating scenarios...")
        for i, pair in enumerate(tqdm(self.scenarios)):
            self.__write_scenario(i, pair, out_path)

    def __write_scenario(self, i, pair, out_path):
        pair[0].write("{}/{}_{}/sc_{}.yaml".format(out_path, self.app.name, self.app.mal_msg_size, i))
        pair[1].write("{}/{}_{}/sc_{}_m.yaml".format(out_path, self.app.name, self.app.mal_msg_size, i))

    def __fit(app_size):
        mc_size = ceil(sqrt(app_size + Generator.__TASK_OVERHEAD))
        fits = []

        # Possible fit: mc_size*mc_size (square)
        fits.append(Slots(mc_size, mc_size))

        # Possible fit: rectangular
        if (mc_size*(mc_size-1) - Generator.__TASK_OVERHEAD) >= app_size:
            fits.append(Slots(mc_size, mc_size-1))
            
        # Possible fit: half the square size
        if (mc_size*(mc_size + 1)/2 - (Generator.__TASK_OVERHEAD-1)) >= app_size:
            fits.append(Slots(mc_size, mc_size, rem_top_diag=True))

        # Possible fit: half of the bigger square
        if ((mc_size + 1)*(mc_size + 2)/2 - (Generator.__TASK_OVERHEAD-1)) >= app_size:
            fits.append(Slots(mc_size+1, mc_size+1, rem_top_diag=True))
            
        return sorted(fits)[0]
