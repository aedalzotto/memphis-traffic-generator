from pandas import read_csv
from .extractor import Extractor

class SafeExtract:
    def __init__(self, ntc, mtc, test):
        self.ntc = ntc
        df = read_csv(test)
        scen_idx = list(df["scenario"].unique())
        self.extractor = Extractor(ntc, None, None, mtc, rtd_scens=scen_idx)

    def extract(self):
        self.extractor.extract("{}_rtd.csv".format(self.ntc[3:]))

        # We need to extract metrics too!
