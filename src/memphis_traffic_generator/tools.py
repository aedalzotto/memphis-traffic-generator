from os import listdir

def __index_of(scenario):
    return int(scenario.split("/")[-1].split(".")[0].split("_")[1])

def get_scenarios(base, with_base=False, with_test=False, with_ht=False, with_mapp=False, with_fp=False, keep_yaml=False):
    scenarios = sorted(["{}/{}".format(base, scenario) for scenario in listdir(base) if scenario.startswith("sc_")])

    # Keep everything not base        
    if not with_base:
        scenarios = list(filter(lambda scenario: scenario.endswith(("_ht{}".format(".yaml" if keep_yaml else ""), "_rtd{}".format(".yaml" if keep_yaml else ""), "_fp{}".format(".yaml" if keep_yaml else ""))), scenarios))

    # Remove everything test-related
    if not with_test:
        scenarios = list(filter(lambda scenario: not scenario.endswith(("_normal_rtd{}".format(".yaml" if keep_yaml else ""), "_ht{}".format(".yaml" if keep_yaml else ""))), scenarios))

    # Remove everything HT-related
    if not with_ht:
        scenarios = list(filter(lambda scenario: not scenario.endswith(("_ht_rtd{}".format(".yaml" if keep_yaml else ""), "_ht_rtd_fp{}".format(".yaml" if keep_yaml else ""))), scenarios))

    # Remove everything with Mapp
    if not with_mapp:
        scenarios = list(filter(lambda scenario: not scenario.endswith(("_mapp_rtd{}".format(".yaml" if keep_yaml else ""), "_mapp_rtd_fp{}".format(".yaml" if keep_yaml else ""))), scenarios))

    # Remove everything with FP
    if not with_fp:
        scenarios = list(filter(lambda scenario: not scenario.endswith("_fp{}".format(".yaml" if keep_yaml else "")), scenarios))
    else:
        scenarios = list(filter(lambda scenario: not scenario.endswith("_rtd{}".format(".yaml" if keep_yaml else "")), scenarios))

    return scenarios
