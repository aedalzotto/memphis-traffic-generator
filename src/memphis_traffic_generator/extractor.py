import pandas as pd
from tqdm import tqdm
from joblib import Parallel, delayed
from memphis_traffic_analyzer.dmni import DMNI
from .tools import get_scenarios
from .mapping import Mapping

class Extractor:
    def __init__(self, testcase, lower_bound, upper_bound, testcase_m=None):
        self.testcase = testcase
        self.scenarios = get_scenarios(testcase, lower_bound, upper_bound)
        if testcase_m is None:
            self.scenarios_m = None
        else:
            self.scenarios_m = get_scenarios(testcase_m, lower_bound, upper_bound)

    def __get_dmni(scenario):
        malicious_tc = scenario.split("/")[-2].endswith("_m")
        df = DMNI(scenario).df
        malicious_sc = scenario.endswith("_m")
        df["scenario"]  = scenario.split("/")[-1].split("_")[1]
        df["malicious"] = malicious_sc or malicious_tc
        df.drop(df[df["app"] == 0].index, inplace=True)
        if malicious_sc:
            df.drop(df[df["app"] == 1].index, inplace=True)
        df.drop(["app"], axis=1, inplace=True)
        mapping = Mapping(scenario, ["malicious_rand"])
        df["hops"] = [Mapping.distance(mapping[df.loc[i, "prod"]], mapping[df.loc[i, "cons"]]) for i in df.index]
        df.loc[0, "rel_timestamp"] = 0
        df.loc[1:, "rel_timestamp"] = df.loc[1:, "timestamp"] - df.loc[0, "timestamp"]
        return df

    def extract(self, output):
        print("Extracting DMNI logs from scenarios...")
        scen_list = self.scenarios
        if self.scenarios_m is not None:
            scen_list += self.scenarios_m
        dmnis = Parallel(n_jobs=-1)(delayed(Extractor.__get_dmni)(scenario) for scenario in tqdm(scen_list))
        df = pd.concat(dmnis, ignore_index=True)

        if output is None:
            output = "{}.csv".format(self.testcase[3:])

        df.to_csv(output, index=False)
