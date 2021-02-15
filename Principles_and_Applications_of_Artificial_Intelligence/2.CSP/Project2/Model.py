class Node:
    def __init__(self, loc, num, color, domain):
        self.loc = loc
        self.num = num
        self.color = color
        self.domain = domain


class State:
    def __init__(self, state, parent=None):
        self.state = state
        self.replicate_state = parent
