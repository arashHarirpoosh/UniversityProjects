from Project1.Game import *
from Project1.Node import Node


class Search:
    def __init__(self, initial_state, m, n):
        self.initial_state = initial_state
        self.m = m
        self.n = n
        self.frontier = []
        self.explored = []

    # Find Number Of Different Colors That Are In One Row
    def calculate_different_colors(self, row):
        row_colors = [x[1] for x in row]
        return len(set(row_colors)) - 1

    # Find Number Of Cards That Are Not In a Appropriate Position According To Card Numbers
    def calculate_disordered_cards(self, row):
        row_size = len(row)
        wrong_places = 0
        if row[0][0] < row[1][0]:
            wrong_places += 1
        if row[row_size - 2][0] < row[row_size - 1][0]:
            wrong_places += 1
        for i in range(1, row_size - 1):
            if not (row[i + 1][0] < row[i][0] < row[i - 1][0]):
                wrong_places += 1
        return wrong_places

    # Calculate The Heuristic Value For A Node
    def calculate_heuristic(self, node):
        heuristic = 0
        size = []
        for r in node:
            size.append(len(r))
            if len(r) > 1:
                predicted_price = 0.7 * max(self.calculate_different_colors(r),
                                            self.calculate_disordered_cards(r))
                heuristic += predicted_price

        all_sizes = sorted(size)
        for i in all_sizes:
            if i < self.n:
                heuristic += 0.3 * min(abs(self.n-i), i)
        return heuristic

    # Find Node With Minimum Distance To Explore
    def find_min_node(self):
        selected_node = [None, float('inf')]
        front = self.frontier
        for s in front:
            if s[1] < selected_node[1]:
                selected_node = s
        return selected_node

    # Search In Game With A* Graph Search
    def AStar_GraphSearch(self):
        node = Node(self.initial_state, (), None)
        distance = self.calculate_heuristic(node.info) + 0
        m = self.m
        if goal_test(node.info, m):
            return node
        self.frontier.append([node, distance, 0])

        while len(self.frontier) != 0:
            node = self.find_min_node()
            self.frontier.remove(node)
            par = node[0]
            dist = node[2]
            self.explored.append(node)
            node = node[0].info
            all_actions = actions(node)
            for action in all_actions:
                child = Node(do_action(node, action[0], action[1]), action, par)
                all_front_node = [x[0].info for x in self.frontier]
                if child.info not in (self.explored or all_front_node):
                    if goal_test(child.info, m):
                        return child

                    if child.info not in all_front_node:
                        distance = self.calculate_heuristic(child.info) + dist
                        self.frontier.append([child, distance, dist + 1])

        return []

    # Find All The Ancestors Of Result Node
    def final_actions(self, final_node):
        p = final_node.parent
        all_actions = []
        while p is not None:
            all_actions.append(p)
            p = p.parent
        return all_actions

    # Print The Path Of Final Solution
    def print_actions(self, all_actions, final_node):
        size = len(all_actions)
        for i in range(size - 1, -1, -1):
            print('Step: ', size - i - 1)
            if i > 0:
                print('Node:')
                for n in all_actions[i].info:
                    print(n)
                print('Action: ', all_actions[i - 1].action)
            else:
                print('Node: ')
                for n in all_actions[i].info:
                    print(n)
                print('Action: ', final_node.action)
            print('-' * 50)
        print('Final Node: ')
        for n in final_node.info:
            print(n)
