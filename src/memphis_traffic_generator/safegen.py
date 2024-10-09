from .builder import Builder
from .simulator import Simulator
from pandas import read_csv

class SafeGen:
    def __init__(self, ntc, mtc, apps, scenarios, test):
        self.n_builder = Builder(ntc, apps, scenarios)
        self.m_builder = Builder(mtc, apps, scenarios)

        df = read_csv(test)
        self.scen_idx = list(df["scenario"].unique())

    def build(self):
        self.n_builder.build_tc() # Rebuild tc to ensure ODA is up to date
        self.n_builder.build_sc(self.scen_idx)

        self.m_builder.build_tc()
        self.m_builder.build_sc(self.scen_idx)
    