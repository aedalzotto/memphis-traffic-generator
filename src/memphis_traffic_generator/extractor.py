import pandas as pd
from tqdm import tqdm
from joblib import Parallel, delayed
from memphis_traffic_analyzer.dmni import DMNI
from .tools import get_scenarios
from .mapping import Mapping

class Extractor:
    def __init__(self, testcase, lower_bound, upper_bound):
        self.testcase = testcase
        self.scenarios = get_scenarios(testcase, lower_bound, upper_bound)

    def __get_dmni(scenario):
        df = DMNI(scenario).df
        malicious = scenario.endswith("_m")
        df["scenario"]  = scenario.split("/")[-1].split("_")[1]
        df["malicious"] = malicious
        df.drop(df[df["app"] == 0].index, inplace=True)
        if malicious:
            df.drop(df[df["app"] == 1].index, inplace=True)
        df.drop(["app"], axis=1, inplace=True)
        mapping = Mapping(scenario)
        df["hops"] = [Mapping.distance(mapping[df.loc[i, "prod"]], mapping[df.loc[i, "cons"]]) for i in df.index]
        df.loc[0, "rel_timestamp"] = 0
        df.loc[1:, "rel_timestamp"] = df.loc[1:, "timestamp"] - df.loc[0, "timestamp"]
        return df

    def extract(self, output):
        print("Extracting DMNI logs from scenarios...")
        dmnis = Parallel(n_jobs=-1)(delayed(Extractor.__get_dmni)(scenario) for scenario in tqdm(self.scenarios))
        df = pd.concat(dmnis, ignore_index=True)

        if output is None:
            output = "{}.csv".format(self.testcase[3:])

        df.to_csv(output, index=False)
