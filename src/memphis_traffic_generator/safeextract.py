from pandas import read_csv
from .extractor import Extractor
from pandas import DataFrame, concat
from yaml import safe_load
from yaspin import yaspin

class SafeExtract:
    def __init__(self, ntc, mtc, test):
        self.ntc = ntc
        self.threshold = test.split("_")[-3]
        df = read_csv(test)
        self.scen_idx = list(df["scenario"].unique())
        self.extractor = Extractor(ntc, None, None, mtc, rtd_scens=self.scen_idx)

    def extract(self):
        df_lat = DataFrame(columns=['scenario', 'n_inf', 'avg_latency'])
        df_inf = DataFrame(columns=['scenario', 'rel_timestamp', 'prod', 'cons', 'det_latency', 'anomaly'])
        df_end = DataFrame(columns=['scenario', 'rtd', 'beggining', 'end'])

        with yaspin(text="Extracting simulation data...") as spinner:
            for scenario in self.scen_idx:
                path_n = "{}/rtd_{}".format(self.ntc, scenario)
                scen_n = "{}/sc_{}".format(self.ntc, scenario)
                path_m = "{}_m/rtd_{}".format(self.ntc, scenario)
                
                with open("{}/rtd_{}.yaml".format(path_m, scenario), "r") as f:
                    yaml = safe_load(f)
                for task in yaml["management"]:
                    if task["task"] == "mapper_task":
                        mapper = task["static_mapping"]
                    elif task["task"].startswith("safe-") and task["task"].split("-")[-1] != "monitor":
                        safe = task["static_mapping"]
            
                inferences = []
                with open("{}/log/log{}x{}.txt".format(path_m, safe[0], safe[1]), "r") as f:
                    for line in f:
                        if line[0] == "$":
                            line = line.split("_")[-1]
                            tokens = line.split("\t")
                            if tokens[0] == "IT":
                                df_lat = concat(
                                    [
                                        DataFrame(
                                            [
                                                [
                                                    scenario,
                                                    int(tokens[1]),
                                                    int(tokens[2])
                                                ]
                                            ], 
                                            columns=df_lat.columns
                                        ), 
                                        df_lat
                                    ], 
                                    ignore_index=True
                                )

                with open("{}/debug/safe/{}x{}.txt".format(path_m, safe[0], safe[1]), "r") as f:
                    for line in f:
                        tokens = line.split(",")
                        df_inf = concat(
                            [
                                DataFrame(
                                    [
                                        [
                                            scenario,
                                            int(tokens[0]),
                                            int(tokens[1]), 
                                            int(tokens[2]), 
                                            int(tokens[3]),
                                            int(tokens[4])
                                        ]
                                    ], 
                                    columns=df_inf.columns
                                ), 
                                df_inf
                            ], 
                            ignore_index=True
                        )

                with open("{}/log/log{}x{}.txt".format(path_n, mapper[0], mapper[1]), "r") as f:
                    beggining = 0
                    end = 0
                    for line in f:
                        if line[0] == "$":
                            line = line.split("_")[-1]
                            tokens = line.split(" ")
                            if tokens[0] == "RELEASE" and int(tokens[6]) == 1:
                                beggining = tokens[3]
                            elif tokens[0] == "App" and int(tokens[1]) == 1:
                                end = tokens[5]
                    df_end = concat(
                        [
                            DataFrame(
                                [
                                    [
                                        scenario,
                                        True, 
                                        int(beggining), 
                                        int(end)
                                    ]
                                ], 
                                columns=df_end.columns
                            ), 
                            df_end
                        ], 
                        ignore_index=True
                    )

                with open("{}/log/log{}x{}.txt".format(scen_n, mapper[0], mapper[1]), "r") as f:
                    beggining = 0
                    end = 0
                    for line in f:
                        if line[0] == "$":
                            line = line.split("_")[-1]
                            tokens = line.split(" ")
                            if tokens[0] == "RELEASE" and int(tokens[6]) == 1:
                                beggining = tokens[3]
                            elif tokens[0] == "App" and int(tokens[1]) == 1:
                                end = tokens[5]
                    df_end = concat(
                        [
                            DataFrame(
                                [
                                    [
                                        scenario,
                                        False, 
                                        int(beggining), 
                                        int(end)
                                    ]
                                ], 
                                columns=df_end.columns
                            ), 
                            df_end
                        ], 
                        ignore_index=True
                    )
            spinner.ok()

        df_lat.to_csv("{}_{}_lat.csv".format(self.ntc[3:], self.threshold), index=False)
        df_inf.to_csv("{}_{}_inf.csv".format(self.ntc[3:], self.threshold), index=False)
        df_end.to_csv("{}_{}_end.csv".format(self.ntc[3:], self.threshold), index=False)

        self.extractor.extract("{}_rtd_{}.csv".format(self.ntc[3:], self.threshold))

        print("Simulation data exported to {}_{}_{{lat, inf, end}}.csv".format(self.ntc[3:], self.threshold))
