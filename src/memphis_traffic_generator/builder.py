from subprocess import run, DEVNULL
from os import listdir
from tqdm import tqdm
from yaspin import yaspin
from joblib import Parallel, delayed
from .tools import get_scenarios

class Builder:
    def __init__(self, testcase, apps, scenarios, with_base, with_test, with_ht, with_mapp, with_fp):
        self.name      = scenarios
        self.testcase  = testcase
        self.apps      = apps
        with yaspin(text="Listing scenarios...") as spinner:
            self.scenarios = get_scenarios(scenarios, with_base, with_test, with_ht, with_mapp, with_fp, keep_yaml=True)
            spinner.ok()

    def __build_tc(self):
        with yaspin(text="Building testcase...") as spinner:
            with open("{}.log".format(self.name), "w") as log:
                if run(["memphi5", "testcase", self.testcase], stdout=log, stderr=log).returncode != 0:
                    raise Exception("Error building testcase. Check log for more information.")
            spinner.ok()

        with yaspin(text="Building applications...") as spinner:
            with open("{}.log".format(self.name), "a") as log:
                if run(["memphi5", "applications", self.testcase[:-5], self.apps], stdout=log).returncode != 0:
                    raise Exception("Error building applications. Check log for more information.")
            spinner.ok()

    def __build_sc(self):
        print("Building scenarios...")
        Parallel(n_jobs=-1)(delayed(Builder.__build_scenario)(self.testcase[:-5], scenario) for scenario in tqdm(self.scenarios))

    def build(self):
        self.__build_tc()
        self.__build_sc()
        print("Built to {}".format(self.testcase[:-5]))

    def __build_scenario(testcase, scenario):
        if run(["memphi5", "scenario", testcase, scenario], stdout=DEVNULL).returncode != 0:
            raise Exception("Error building scenario {}/{}".format(testcase, scenario))
