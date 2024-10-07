from os import listdir

def __index_of(scenario):
    return int(scenario.split("/")[-1].split(".")[0].split("_")[1])

def get_scenarios(testcase, lower_bound=None, upper_bound=None, rtd_scens=None):
    start_tks = "sc_" if rtd_scens is None else "rtd_"
    scenarios = sorted(["{}/{}".format(testcase, scenario) for scenario in listdir(testcase) if scenario.startswith(start_tks)])

    if lower_bound is not None:
        scenarios = list(filter(lambda scenario: __index_of(scenario) >= int(lower_bound), scenarios))

    if upper_bound is not None:
        scenarios = list(filter(lambda scenario: __index_of(scenario) < int(upper_bound), scenarios))

    if rtd_scens is not None:
        scenarios = list(filter(lambda scenario: __index_of(scenario) in rtd_scens, scenarios))

    return scenarios

def sc_idx(scenario):
    return int(scenario.split("_")[-1].split(".")[0])
