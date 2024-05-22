class parameter:
    def __init__(self, name, min, max):
        self.name = name
        self.min = min
        self.max = max

    def in_bounds(self, value):
        if value < self.min or value > self.max:
            return(False)
        return(True)
    
    def width(self):
        return(self.max - self.min + 1)