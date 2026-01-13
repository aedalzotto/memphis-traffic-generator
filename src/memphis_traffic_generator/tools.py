from os import listdir

def __index_of(scenario):
    return int(scenario.split("/")[-1].split(".")[0].split("_")[1])

def get_scenarios(testcase, no_base=False, with_ht=False, with_mapp=False):
    scenarios = sorted(["{}/{}".format(testcase, scenario) for scenario in listdir(testcase) if scenario.startswith("sc_")])

    if no_base:
        scenarios = list(filter(lambda scenario: (scenario.endswith("_ht") or scenario.endswith("_mapp")), scenarios))
        
    if not with_ht:
        scenarios = list(filter(lambda scenario: not scenario.endswith("_ht"), scenarios))

    if not with_mapp:
        scenarios = list(filter(lambda scenario: not scenario.endswith("_mapp"), scenarios))

    return scenarios
