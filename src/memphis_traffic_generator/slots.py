class Slots:
    def __init__(self, x, y, rem_top_diag=False, ht=False):
        self._x = x
        self._y = y

        self.slots = [*range(0, x*y)]

        if rem_top_diag:
            top_diag = [i for i in self.slots if Slots.to_y(i, x) > Slots.to_x(i, x)]
            for i in top_diag:
                self.slots.remove(i)
        else:
            self.slots.remove(x*(y-1)) # Remove mapper
        
        if not ht:
            self.slots.remove(0)       # Remove prod
            self.slots.remove(x*y - 1) # Remove cons

    def __len__(self):
        return len(self.slots)
    
    def __lt__(self, obj): 
        return (len(self) < len(obj))
    
    def __iter__(self):
        return iter(self.slots)
    
    @property
    def x(self):
        return self._x
    
    @property
    def y(self):
        return self._y

    def to_x(i, x):
        return int(i % x)
    
    def to_y(i, x):
        return int(i / x)
