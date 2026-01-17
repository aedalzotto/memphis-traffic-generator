import pandas as pd
from tqdm import tqdm
from joblib import Parallel, delayed
from memphis_traffic_analyzer.dmni import DMNI
from .tools import get_scenarios
from .mapping import Mapping
from os import listdir
from numpy import int32

class Extractor:
    def __init__(self, testcase, with_base, test_ht, test_rtd, with_ht, with_mapp, with_fp):
        self.testcase = testcase

        self.train = None
        if with_base:
            self.train = get_scenarios(testcase, with_base=True)

        self.test_ht  = None
        self.test_rtd = None
        if test_ht or test_rtd:
            test  = get_scenarios(testcase, with_test=True)
            if test_ht:
                self.test_ht  = list(filter(lambda scenario: scenario.endswith("_ht"), test))
            if test_rtd:
                self.test_rtd = list(filter(lambda scenario: scenario.endswith("_normal_rtd"), test))

        self.ht = None
        if with_ht:
            self.ht = get_scenarios(testcase, with_ht=True, with_fp=with_fp)

        self.mapp = None
        if with_mapp:
            self.mapp = get_scenarios(testcase, with_mapp=True, with_fp=with_fp)

        self.with_fp = with_fp

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
    
    def __get_mapping_score(mapping, scenario):
        id = 0
        # print("{}/log/log{}x{}.txt".format(scenario, mapping.management["mapper_task"][0], mapping.management["mapper_task"][1]), 'r')
        with open("{}/log/log{}x{}.txt".format(scenario, mapping.management["mapper_task"][0], mapping.management["mapper_task"][1]), 'r') as f:
            for line in f:
                tks = line.split("_")
                if len(tks) >= 5 and tks[0] == "$$$":
                    text = tks[4].split(" ")
                    if text[0] == "Mapped":
                        if id == 0:
                            id += 1
                            continue
                    
                        return int(text[3])
    
    def __get_start(mapping, scenario):
        id = 1
        # print("{}/log/log{}x{}.txt".format(scenario, mapping.management["mapper_task"][0], mapping.management["mapper_task"][1]), 'r')
        with open("{}/log/log{}x{}.txt".format(scenario, mapping.management["mapper_task"][0], mapping.management["mapper_task"][1]), 'r') as f:
            for line in f:
                tks = line.split("_")
                if len(tks) >= 5 and tks[0] == "$$$":
                    text = tks[4].split(" ")
                    if text[0] == "App" and text[2] == "started":
                        if int(text[1]) != id:
                            continue
                    
                        return int(text[4])

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
        
        mapping = Mapping(scenario)
        start = Extractor.__get_start(mapping, scenario)
        df.loc[:, "rel_time"] = int32((df.loc[:, "snd_time"] - start) / 100)
        df['rel_time'] = df['rel_time'].astype('int')
        
        df["hops"] = [Mapping.distance(mapping[df.loc[i, "app"]][df.loc[i, "prod"]], mapping[df.loc[i, "app"]][df.loc[i, "cons"]]) for i in df.index]
        # score = Extractor.__get_mapping_score(mapping, scenario)
        # df["mapping_score"] = [score] * df.shape[0]

        if appid is not None:
            df.drop(df[df["app"] != int(appid)].index, inplace=True)
            df.reset_index(drop=True, inplace=True)

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
            df["lat_mon"] = 0
            df["lat_pred"] = 0
            df["mal_pred"] = False
            df["inf_lat"] = 0
            df["det_lat"] = 0
            for idx, row in rtd_df.iterrows():
                line = Extractor.__msg_idx(df, row)
                if line is None:
                    pass
                df.loc[line, "lat_mon"] = row["lat_mon"]
                df.loc[line, "lat_pred"] = row["lat_pred"]
                df.loc[line, "mal_pred"] = True
                df.loc[line, "inf_lat"] = row["inf_lat"]
                if malicious:
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
        if self.train is not None:
            print("Extracting DMNI logs from training scenario...")
            train_dmnis = Parallel(n_jobs=-1)(delayed(Extractor.__get_dmni)(
                scenario, 
                1
            ) for scenario in tqdm(self.train))
            train_df = pd.concat(train_dmnis, ignore_index=True)
            train_df.to_csv("{}_train.csv".format(self.testcase[3:]), index=False)
            print("Dataset exported to {}_train.csv".format(self.testcase[3:]))

        if self.test_ht is not None:
            print("Extracting DMNI logs from HT scenario...")
            test_dmnis = Parallel(n_jobs=-1)(delayed(Extractor.__get_dmni)(
                scenario, 
                1, 
                True, 
                False
            ) for scenario in tqdm(self.test_ht))
            test_df = pd.concat(test_dmnis, ignore_index=True)
            test_df.to_csv("{}_test_ht.csv".format(self.testcase[3:]), index=False)
            print("Dataset exported to {}_test_ht.csv".format(self.testcase[3:]))

        if self.test_rtd is not None:
            test_dmnis = Parallel(n_jobs=-1)(delayed(Extractor.__get_dmni)(
                scenario, 
                1, 
                False, 
                True
            ) for scenario in tqdm(self.test_rtd))
            test_df = pd.concat(test_dmnis, ignore_index=True)
            test_df.to_csv("{}_test_rtd.csv".format(self.testcase[3:]), index=False)
            print("Dataset exported to {}_test_rtd.csv".format(self.testcase[3:]))

        if self.ht is not None:
            print("Extracting DMNI logs from HT RTD scenario...")
            rtd_dmnis = Parallel(n_jobs=-1)(delayed(Extractor.__get_dmni)(
                scenario, 
                1, 
                True, 
                True
            ) for scenario in tqdm(self.ht))
            test_df = pd.concat(rtd_dmnis, ignore_index=True)
            test_df.to_csv("{}_rtd_ht{}.csv".format(self.testcase[3:], "_fp" if self.with_fp else ""), index=False)
            print("Dataset exported to {}_rtd_ht{}.csv".format(self.testcase[3:], "_fp" if self.with_fp else ""))

        if self.mapp is not None:
            print("Extracting DMNI logs from MAPP RTD scenario...")
            rtd_dmnis = Parallel(n_jobs=-1)(delayed(Extractor.__get_dmni)(
                scenario, 
                2, 
                False, 
                True
            ) for scenario in tqdm(self.mapp))
            test_df = pd.concat(rtd_dmnis, ignore_index=True)
            test_df.to_csv("{}_rtd_mapp{}.csv".format(self.testcase[3:], "_fp" if self.with_fp else ""), index=False)
            print("Dataset exported to {}_rtd_mapp{}.csv".format(self.testcase[3:], "_fp" if self.with_fp else ""))
