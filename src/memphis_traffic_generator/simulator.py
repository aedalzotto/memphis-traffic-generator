from tqdm import tqdm
from joblib import Parallel, delayed
from subprocess import run
from yaspin import yaspin
from time import perf_counter
from .tools import get_scenarios

class Simulator:
    def __init__(self, testcase, with_base, with_test, with_ht, with_mapp, with_fp):
        with yaspin(text="Listing scenarios...") as spinner:
            self.scenarios = get_scenarios(testcase, with_base, with_test, with_ht, with_mapp, with_fp)
            spinner.ok()

    def simulate(self):
        print("Simulating...")
        then = perf_counter()
        Parallel(n_jobs=-1)(delayed(Simulator.__simulate_scenario)(scenario) for scenario in tqdm(self.scenarios))
        now = perf_counter()
        print("Simulated {} mappings in {} seconds".format(len(self.scenarios), int(now-then)))

    def __simulate_scenario(scenario):
        with open("{}/sim.log".format(scenario), "w") as log:
            if run(["memphi5", "simulate", scenario, "--nogui"], stdout=log).returncode != 0:
                raise Exception("Error simulating scenario. Check log for details.")
