class Task:
    def __init__(self, name, mapping=None):
        self._mapping = mapping
        self.name    = name
    
    @property
    def x(self):
        return self._mapping[0]
    
    @property
    def y(self):
        return self._mapping[1]
