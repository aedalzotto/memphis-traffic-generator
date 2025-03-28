from yaml import safe_load
from .task import Task

class Mapping:
    def __init__(self, scenario):
        yaml = safe_load(open("{}/{}.yaml".format(scenario, scenario.split('/')[-1]), 'r'))
        apps = yaml["apps"]

        self._tasks = {}
        for idx, app in enumerate(apps):
            self._tasks[idx+1] = {}
            for i, task in enumerate(sorted(app["static_mapping"])):
                x = app["static_mapping"][task][0]
                y = app["static_mapping"][task][1]
                self._tasks[idx+1][i] = Task(task, (x, y))
        
    def __getitem__(self, key):
        return self._tasks[key]

    def distance(prod, cons):
        return abs(prod.x - cons.x) + abs(prod.y - cons.y)
