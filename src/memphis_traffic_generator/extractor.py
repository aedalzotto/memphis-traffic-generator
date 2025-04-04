import pandas as pd
from tqdm import tqdm
from joblib import Parallel, delayed
from memphis_traffic_analyzer.dmni import DMNI
from .tools import get_scenarios
from .mapping import Mapping
from os import listdir

class Extractor:
    def __init__(self, testcase, no_base, with_rtd, appid=None):
        self.testcase = testcase
        train_test = get_scenarios(testcase, no_base, False)
        self.train = list(filter(lambda scenario: not scenario.endswith("_m"), train_test))
        self.test  = list(filter(lambda scenario: scenario.endswith("_m"), train_test))
        self.rtd   = get_scenarios(testcase, True, with_rtd)
        self.appid = appid

    def __msg_idx(df, row):
        app = (row["prod"] >> 8)
        if (row["cons"] >> 8) != app:
            return None
        prod = row["prod"] & 0xFF
        cons = row["cons"] & 0xFF
        line = df[(df["snd_time"] == row["snd_time"]) & (df["app"] == app) & (df["prod"] == prod) & (df["cons"] == cons)].index
        if df.iloc[line].shape[0] != 1:
            raise Exception("Could not match HT to message")
        return line

    def __get_dmni(scenario, appid, malicious=False, rtd=False):
        if malicious:
            ht_df = Extractor.__get_ht(scenario)

        if rtd:
            rtd_df = Extractor.__get_rtd(scenario)

        df = DMNI(scenario).df
        scen_name = scenario.split("/")[-1]
        try:
            scen_name = scen_name.split("_")[1]
        except:
            pass
        df["scenario"] = scen_name
        
        df.loc[0,  "rel_time"] = 0
        df.loc[1:, "rel_time"] = df.loc[1:, "snd_time"] - df.loc[0, "snd_time"]
        df['rel_time'] = df['rel_time'].astype('int')

        mapping = Mapping(scenario)
        df["hops"] = [Mapping.distance(mapping[df.loc[i, "app"]][df.loc[i, "prod"]], mapping[df.loc[i, "app"]][df.loc[i, "cons"]]) for i in df.index]

        if appid is not None:
            df.drop(df[df["app"] != int(appid)].index, inplace=True)

        if malicious:
            df["ht_time"] = 0
            df["malicious"] = False
            df["mal_cycles"] = 0
            for idx, row in ht_df.iterrows():
                line = Extractor.__msg_idx(df, row)
                if line is None:
                    pass
                df.loc[line, "ht_time"] = row["ht_time"]
                df.loc[line, "malicious"]  = True
                df.loc[line, "mal_cycles"] = row["cycles"]

        if rtd:
            df["mal_pred"] = False
            df["inf_lat"] = 0
            df["det_lat"] = 0
            for idx, row in rtd_df.iterrows():
                line = Extractor.__msg_idx(df, row)
                if line is None:
                    pass
                df.loc[line, "mal_pred"] = True
                df.loc[line, "inf_lat"] = row["inf_lat"]
                df.loc[line, "det_lat"] = row["inf_time"] - df.loc[line, "ht_time"]

        return df

    def __get_ht(scenario):
        path = "{}/debug/link".format(scenario)
        logs = ["{}/{}".format(path, s) for s in listdir(path)]
        df = pd.concat(map(pd.read_csv, logs), ignore_index=True)
        return df
    
    def __get_rtd(scenario):
        path = "{}/debug/safe".format(scenario)
        logs = ["{}/{}".format(path, s) for s in listdir(path)]
        df = pd.concat(map(pd.read_csv, logs), ignore_index=True)
        return df

    def extract(self):
        if len(self.train) > 0:
            print("Extracting DMNI logs from training scenario...")
            train_dmnis = Parallel(n_jobs=-1)(delayed(Extractor.__get_dmni)(
                scenario, 
                self.appid
            ) for scenario in tqdm(self.train))
            train_df = pd.concat(train_dmnis, ignore_index=True)
            train_df.to_csv("{}_train.csv".format(self.testcase[3:]), index=False)

            print("Extracting DMNI logs from test scenario...")
            test_dmnis = Parallel(n_jobs=-1)(delayed(Extractor.__get_dmni)(
                scenario, 
                self.appid, 
                True, 
                False
            ) for scenario in tqdm(self.test))
            test_df = pd.concat(test_dmnis, ignore_index=True)
            test_df.to_csv("{}_test.csv".format(self.testcase[3:]), index=False)

            print("Dataset exported to {}_{{train,test}}.csv".format(self.testcase[3:]))

        if len(self.rtd) > 0:
            print("Extracting DMNI logs from RTD scenario...")
            rtd_dmnis = Parallel(n_jobs=-1)(delayed(Extractor.__get_dmni)(
                scenario, 
                self.appid, 
                True, 
                True
            ) for scenario in tqdm(self.rtd))
            test_df = pd.concat(rtd_dmnis, ignore_index=True)
            test_df.to_csv("{}_rtd.csv".format(self.testcase[3:]), index=False)

            print("Dataset exported to {}_rtd.csv".format(self.testcase[3:]))
