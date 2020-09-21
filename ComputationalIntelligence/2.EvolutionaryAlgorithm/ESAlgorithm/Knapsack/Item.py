class Item:
    def __init__(self, weight, value):
        self.weight = int(weight)
        self.value = int(value)

    def worthiness(self, item):
        return item.value/item.weight

