from os import listdir
from tqdm import tqdm
from joblib import Parallel, delayed
from subprocess import run

class Simulator:
    def __init__(self, testcase, lower_bound=None, upper_bound=None):
        self.scenarios = sorted(["{}/{}".format(testcase, scenario) for scenario in listdir(testcase) if scenario.startswith("sc_")])
        if lower_bound is not None:
            self.scenarios = list(filter(lambda scenario: Simulator.__index_of(scenario) >= int(lower_bound), self.scenarios))

        if upper_bound is not None:
            self.scenarios = list(filter(lambda scenario: Simulator.__index_of(scenario) < int(upper_bound), self.scenarios))

    def simulate(self):
        print("Simulating...")
        Parallel(n_jobs=-1)(delayed(Simulator.__simulate_scenario)(scenario) for scenario in tqdm(self.scenarios))

    def __simulate_scenario(scenario):
        with open("{}/sim.log".format(scenario), "w") as log:
            if run(["memphi5", "simulate", scenario, "--nogui"], stdout=log).returncode != 0:
                raise Exception("Error simulating scenario. Check log for details.")
            
    def __index_of(scenario):
        return int(scenario.split("/")[-1].split(".")[0].split("_")[1])
