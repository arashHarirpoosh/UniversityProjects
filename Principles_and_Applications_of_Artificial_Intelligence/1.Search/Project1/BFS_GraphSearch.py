from Project1.Game import *
from Project1.Node import Node


class Search:
    def __init__(self, initial_state, m):
        self.initial_state = initial_state
        self.m = m
        self.frontier = []
        self.explored = []

    # Search In Game With BFS Graph Search
    def BFS_GraphSearch(self):
        node = Node(self.initial_state, (), None)
        m = self.m
        if goal_test(node.info, m):
            return node
        self.frontier.append(node)

        while len(self.frontier) != 0:

            node = self.frontier.pop(0)
            par = node
            node = node.info
            self.explored.append(node)
            all_actions = actions(node)
            for action in all_actions:
                child = Node(do_action(node, action[0], action[1]), action, par)
                all_front_node = [x.info for x in self.frontier]
                if child.info not in (self.explored or all_front_node):
                    if goal_test(child.info, m):
                        return child

                    if child.info not in all_front_node:
                        self.frontier.append(child)

        return []

    # Find All The Ancestors Of Result Node
    def final_actions(self, final_node):
        if final_node:
            p = final_node.parent
            all_actions = []
            while p is not None:
                all_actions.append(p)
                p = p.parent
            return all_actions
        return []

    # Print The Path Of Final Solution
    def print_actions(self, all_actions, final_node):
        size = len(all_actions)
        for i in range(size-1, -1, -1):
            print('Step: ', size-i-1)
            if i > 0:
                print('Node:')
                for n in all_actions[i].info:
                    print(n)
                print('Action: ', all_actions[i-1].action)
            else:
                print('Node: ')
                for n in all_actions[i].info:
                    print(n)
                print('Action: ', final_node.action)
            print('-' * 50)
        if final_node:
            print('Final Node: ')
            for n in final_node.info:
                print(n)
        else:
            print('There Is No Solution For This Initial State')
