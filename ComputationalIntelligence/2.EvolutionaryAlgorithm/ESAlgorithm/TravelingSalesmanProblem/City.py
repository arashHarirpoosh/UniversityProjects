import numpy as np
class City:
    def __init__(self,i, x, y):
        self.i = int(i)
        self.x = float(x)
        self.y = float(y)

    # Calculate the distance between two cities
    def distance(self, city):
        xDis = abs(self.x - city.x)
        yDis = abs(self.y - city.y)
        distance = np.sqrt((xDis ** 2) + (yDis ** 2))
        return distance

    def __repr__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"