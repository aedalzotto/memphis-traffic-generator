from os import listdir

def __index_of(scenario):
    return int(scenario.split("/")[-1].split(".")[0].split("_")[1])

def get_scenarios(testcase, lower_bound, upper_bound):
    scenarios = sorted(["{}/{}".format(testcase, scenario) for scenario in listdir(testcase) if scenario.startswith("sc_")])

    if lower_bound is not None:
        scenarios = list(filter(lambda scenario: __index_of(scenario) >= int(lower_bound), scenarios))

    if upper_bound is not None:
        scenarios = list(filter(lambda scenario: __index_of(scenario) < int(upper_bound), scenarios))

    return scenarios
