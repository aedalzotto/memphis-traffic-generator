from math import sqrt

class Slots:
    def __init__(self, minimum):
        size = [(minimum // i, i) for i in range(1, int(sqrt(minimum)) + 1) if minimum % i == 0][-1]
        self._x = size[0]
        self._y = size[1]

        self.slots = [*range(0, self._x*self._y)]

    def __len__(self):
        return len(self.slots)
    
    def __lt__(self, obj): 
        return (len(self) < len(obj))
    
    def __iter__(self):
        return iter(self.slots)
    
    def __to_idx(self, x, y):
        return y*self._x + x
    
    def remove(self, slots):
        slots_idx = [self.__to_idx(slot[0], slot[1]) for slot in slots]
        for idx in slots_idx:
            self.slots.remove(idx)

    def to_xy(self, idx):
        return (int(idx % self.x), int(idx / self._x))

    @property
    def x(self):
        return self._x
    
    @property
    def y(self):
        return self._y
