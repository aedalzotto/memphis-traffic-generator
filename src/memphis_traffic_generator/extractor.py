import pandas as pd
from tqdm import tqdm
from joblib import Parallel, delayed
from memphis_traffic_analyzer.dmni import DMNI
from .tools import get_scenarios, sc_idx
from .mapping import Mapping

class Extractor:
    def __init__(self, testcase, lower_bound, upper_bound, testcase_m=None, scenario=None, rtd_scens=None, appid=None):
        if testcase is None:
            self.testcase = scenario
            self.scenarios = [scenario]
        else:
            self.testcase = testcase
            self.scenarios = get_scenarios(testcase, lower_bound, upper_bound, rtd_scens)
        
        if testcase_m is None:
            self.scenarios_m = None
        else:
            self.scenarios_m = get_scenarios(testcase_m, lower_bound, upper_bound, rtd_scens)

        self.appid = appid

    def __get_dmni(scenario, appid):
        tc_name = scenario.split("/")[-2]
        malicious_tc = tc_name.endswith("_m") or tc_name.endswith("_bad")
        df = DMNI(scenario).df
        malicious_sc = scenario.endswith("_m")
        scen_name = scenario.split("/")[-1]
        try:
            scen_name = scen_name.split("_")[1]
        except:
            pass
        df["scenario"] = scen_name
        df["malicious"] = malicious_sc or malicious_tc
        
        df.loc[0, "rel_timestamp"] = 0
        df.loc[1:, "rel_timestamp"] = df.loc[1:, "timestamp"] - df.loc[0, "timestamp"]
        df['rel_timestamp'] = df['rel_timestamp'].astype('int')

        mapping = Mapping(scenario)
        df["hops"] = [Mapping.distance(mapping[df.loc[i, "app"]][df.loc[i, "prod"]], mapping[df.loc[i, "app"]][df.loc[i, "cons"]]) for i in df.index]

        if malicious_sc:
            df.drop(df[df["app"] == 1].index, inplace=True)
        if appid is not None:
            df.drop(df[df["app"] != int(appid)].index, inplace=True)
        df.drop(["app"], axis=1, inplace=True)

        return df

    def extract(self, output):
        print("Extracting DMNI logs from scenarios...")
        scen_list = self.scenarios
        if self.scenarios_m is not None:
            scen_list += self.scenarios_m
        dmnis = Parallel(n_jobs=-1)(delayed(Extractor.__get_dmni)(scenario, self.appid) for scenario in tqdm(scen_list))
        df = pd.concat(dmnis, ignore_index=True)

        if output is None:
            output = "{}.csv".format(self.testcase[3:])

        df.to_csv(output, index=False)
