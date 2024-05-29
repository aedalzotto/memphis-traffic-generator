from os import listdir
from tqdm import tqdm
from joblib import Parallel, delayed
from memphis_traffic_analyzer.dmni import DMNI
import pandas as pd

class Extractor:
    def __init__(self, testcase):
        self.testcase = testcase
        scenarios = sorted(["{}/{}".format(testcase, scenario) for scenario in listdir(testcase) if scenario.startswith("sc_")])

        print("Extracting DMNI logs from scenarios...")
        dmnis = Parallel(n_jobs=-1)(delayed(Extractor.__get_dmni)(scenario) for scenario in tqdm(scenarios))
        self.df = pd.concat(dmnis, ignore_index=True)

    def __get_dmni(scenario):
        df = DMNI(scenario).df
        malicious = scenario.endswith("_m")
        df["scenario"]  = scenario.split("/")[-1].split("_")[1]
        df["malicious"] = malicious
        df.drop(df[df["app"] == 0].index, inplace=True)
        if malicious:
            df.drop(df[df["app"] == 1].index, inplace=True)
        df.drop(["app"], axis=1, inplace=True)
        return df

    def write(self, output):
        if output is None:
            output = "{}.csv".format(self.testcase[3:])

        self.df.to_csv(output, index=False)
