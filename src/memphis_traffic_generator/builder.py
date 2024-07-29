from subprocess import run, DEVNULL
from os import listdir
from tqdm import tqdm
from yaspin import yaspin
from joblib import Parallel, delayed

class Builder:
    def __init__(self, testcase, apps, scenarios):
        self.name      = scenarios
        self.testcase  = testcase
        self.apps      = apps
        self.scenarios = ["{}/{}".format(scenarios, scenario) for scenario in listdir(scenarios)]

    def build(self):
        with yaspin(text="Building testcase...") as spinner:
            with open("{}.log".format(self.name), "w") as log:
                if run(["memphi5", "testcase", self.testcase], stdout=log).returncode != 0:
                    raise Exception("Error building testcase. Check log for more information.")
            spinner.ok()
    
        with yaspin(text="Building applications...") as spinner:
            with open("{}.log".format(self.name), "a") as log:
                if run(["memphi5", "applications", self.testcase[:-5], self.apps], stdout=log).returncode != 0:
                    raise Exception("Error building applications. Check log for more information.")
            spinner.ok()

        print("Building scenarios...")
        Parallel(n_jobs=-1)(delayed(Builder.__build_scenario)(self.testcase[:-5], scenario) for scenario in tqdm(self.scenarios))

    def __build_scenario(testcase, scenario):
        if run(["memphi5", "scenario", testcase, scenario], stdout=DEVNULL).returncode != 0:
            raise Exception("Error building scenario")
