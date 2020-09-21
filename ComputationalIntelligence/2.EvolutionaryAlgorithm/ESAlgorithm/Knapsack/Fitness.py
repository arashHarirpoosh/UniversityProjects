import numpy as np
class Fitness:
    def __init__(self, bag, Items, maxCap):
        self.bag = bag
        self.Items = Items
        self.maxCapacity = int(maxCap)
        self.fitness = 0

    # Calculate the fitness of individuals
    def bagFitness(self):
        values = [x.value for x in self.Items]
        weights = [x.weight for x in self.Items]
        # print(self.bag, values)
        totalVal = np.sum(self.bag * values)
        totalWeight = np.sum(self.bag * weights)
        if totalWeight <= self.maxCapacity:
            self.fitness = totalVal
        else:
            self.fitness = 0
        # print('v',totalVal, 'w', totalWeight, 'm', self.maxCapacity, 'f', self.fitness)
        return self.fitness

