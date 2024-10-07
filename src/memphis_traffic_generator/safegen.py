from .builder import Builder
from .simulator import Simulator
from pandas import read_csv

class SafeGen:
    def __init__(self, ntc, mtc, apps, scenarios, test):
        self.n_builder = Builder(ntc, apps, scenarios)
        self.m_builder = Builder(mtc, apps, scenarios)
        self.tc_name = ntc.split(".")[-2]

        df = read_csv(test)
        self.scen_idx = list(df["scenario"].unique())
        self.n_simulator = Simulator(ntc.split(".")[-2], rtd_scens=self.scen_idx)
        self.m_simulator = Simulator(mtc.split(".")[-2], rtd_scens=self.scen_idx)

    def generate(self):
        self.__build()
        self.__simulate()

    def __build(self):
        self.n_builder.build_tc() # Rebuild tc to ensure ODA is up to date
        self.n_builder.build_sc(self.scen_idx)

        self.m_builder.build_tc()
        self.m_builder.build_sc(self.scen_idx)

    def __simulate(self):
        self.n_simulator.simulate()
        self.m_simulator.simulate()
    