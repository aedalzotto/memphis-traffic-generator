from tqdm import tqdm
from joblib import Parallel, delayed
from subprocess import run
from .tools import get_scenarios

class Simulator:
    def __init__(self, testcase, lower_bound=None, upper_bound=None, rtd_scens=None):
        self.scenarios = get_scenarios(testcase, lower_bound, upper_bound, rtd_scens)

    def simulate(self):
        print("Simulating...")
        Parallel(n_jobs=-1)(delayed(Simulator.__simulate_scenario)(scenario) for scenario in tqdm(self.scenarios))

    def __simulate_scenario(scenario):
        with open("{}/sim.log".format(scenario), "w") as log:
            if run(["memphi5", "simulate", scenario, "--nogui"], stdout=log).returncode != 0:
                raise Exception("Error simulating scenario. Check log for details.")
