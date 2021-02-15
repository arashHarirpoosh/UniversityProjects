from Project1.Game import *
from Project1.Node import Node


class Search:
    def __init__(self, initial_state, m):
        self.initial_state = initial_state
        self.m = m
        self.explored = 0
        self.generate = 0

    # Search The Node's With DFS And Limited Depth
    def recursive_DLS(self, node, limit):
        m = self.m
        if goal_test(node.info, m):
            return ['goal', node]
        elif limit == 0:
            return ['cutoff', node]
        else:
            par = node
            cutoff_occurred = False
            all_actions = actions(node.info)
            self.explored += 1
            for action in all_actions:
                child = Node(do_action(node.info, action[0], action[1]), action, par)
                self.generate += 1
                result = self.recursive_DLS(child, limit-1)
                res_state = result[0]
                if res_state == 'cutoff':
                    cutoff_occurred = True
                elif res_state != 'fail':
                    return result
            if cutoff_occurred:
                return ['cutoff', node]
            else:
                return ['fail']

    # DLS Search
    def depth_limited_search(self, limit):
        par = Node(self.initial_state, (), None)
        return self.recursive_DLS(par, limit)

    # Search In Game With IDS Tree Search
    def iterative_deepening_search(self, initial_depth):
        limit = initial_depth
        while 1:
            result = self.depth_limited_search(limit)
            limit += 1
            if result[0] != 'cutoff':
                return result

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
        print('Final Node: ')
        for n in final_node.info:
            print(n)
