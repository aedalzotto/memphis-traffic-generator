from .simulator import Simulator
from pandas import read_csv

class SafeSim:
    def __init__(self, ntc, mtc, test):
        df = read_csv(test)
        self.scen_idx = list(df["scenario"].unique())
        self.n_simulator = Simulator(ntc, rtd_scens=self.scen_idx)
        self.m_simulator = Simulator(mtc, rtd_scens=self.scen_idx)

    def simulate(self):
        self.n_simulator.simulate()
        self.m_simulator.simulate()
