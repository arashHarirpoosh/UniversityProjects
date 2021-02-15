from copy import deepcopy
from Project2.Model import *


class CSP:
    def __init__(self, initial_state, m, n):
        self.current_state = initial_state
        # self.replicate_state = None
        self.constraint_of_nodes = {}
        self.assigned_nodes = []
        self.loc_assigned = []
        self.m = int(m)
        self.n = int(n)
        self.used_domain = {}

    def find_constraints_of_nodes(self):
        dim = len(self.current_state.state)
        for r in range(dim):
            for c in range(dim):
                row_const_num = [(r, i) for i in range(dim) if i != c]
                col_const_num = [(i, c) for i in range(dim) if i != r]
                num_constraints = row_const_num + col_const_num
                row_const_color = [(r, i) for i in range(max(0, c - 1), min(dim, c + 2)) if i != c]
                col_const_color = [(i, c) for i in range(max(0, r - 1), min(dim, r + 2)) if i != r]
                color_constraints = row_const_color + col_const_color
                key = self.current_state.state[r][c].loc
                value = {
                    'numeric_constraints': num_constraints,
                    'color_constraints': color_constraints
                }
                self.constraint_of_nodes[key] = value
                self.used_domain[key] = []

    def num_consistency(self, csp, changed_node):
        # self.current_state.replicate_state = self.current_state
        # changed_node = self.current_state.state[r][c]
        if changed_node.num is not None:
            num_constraints = self.constraint_of_nodes[changed_node.loc]['numeric_constraints']
            for p in num_constraints:
                curr_node = csp.state[p[0]][p[1]]
                # if not curr_node.is_assigned():
                # if curr_node not in self.assigned_nodes:
                if curr_node.loc not in self.loc_assigned:
                    curr_node.domain = curr_node.domain[curr_node.domain[:, 0] != changed_node.num]
                    if changed_node.color and curr_node.num is not None:
                        if changed_node.num > curr_node.num:
                            curr_node.domain = curr_node.domain[changed_node.color > curr_node.domain[:, 1]]
                        else:
                            curr_node.domain = curr_node.domain[changed_node.color < curr_node.domain[:, 1]]
                        if curr_node.num == self.n:
                            curr_node.domain = curr_node.domain[curr_node.domain[:, 1] > 1]
                        elif curr_node.num == 1:
                            curr_node.domain = curr_node.domain[curr_node.domain[:, 1] < self.m]

                    if len(curr_node.domain) == 0:
                        # print('backtrack')
                        return False, csp
        return True, csp

    def color_consistency(self, csp, changed_node):
        # changed_node = self.current_state.state[r][c]
        if changed_node.color is not None:
            color_constraints = self.constraint_of_nodes[changed_node.loc]['color_constraints']
            for p in color_constraints:
                curr_node = csp.state[p[0]][p[1]]
                # if not curr_node.is_assigned():
                # if curr_node not in self.assigned_nodes:
                if curr_node.loc not in self.loc_assigned:
                    curr_node.domain = curr_node.domain[curr_node.domain[:, 1] != changed_node.color]
                    # curr_node.domain = curr_node.domain[curr_node.domain[:, 1]]
                    if changed_node.num is not None and curr_node.color is not None:
                        if changed_node.color > curr_node.color:
                            curr_node.domain = curr_node.domain[changed_node.num > curr_node.domain[:, 0]]
                        else:
                            curr_node.domain = curr_node.domain[changed_node.num < curr_node.domain[:, 0]]
                        if curr_node.color == self.m:
                            curr_node.domain = curr_node.domain[curr_node.domain[:, 0] > 1]
                        elif curr_node.color == 1:
                            curr_node.domain = curr_node.domain[curr_node.domain[:, 0] < self.m]

                    if len(curr_node.domain) == 0:
                        # print('backtrack')
                        return False, csp
        return True, csp

    def forward_checking(self, csp, changed_node):
        num_consistency, new_num_csp = self.num_consistency(csp, changed_node)
        color_consistency, new_csp = self.color_consistency(new_num_csp, changed_node)
        return (num_consistency and color_consistency), new_csp

    def check_consistency(self, csp, new_node):
        # new_node = self.current_state.state[r][c]
        if new_node.num is not None:
            num_constraints = self.constraint_of_nodes[new_node.loc]['numeric_constraints']
            color_constraints = self.constraint_of_nodes[new_node.loc]['color_constraints']
            # print(new_node.is_assigned())
            for p in num_constraints:
                curr_node = csp.state[p[0]][p[1]]
                # if curr_node.is_assigned():
                # if curr_node in self.assigned_nodes:
                if curr_node.loc in self.loc_assigned:
                    priority_constraints_high, priority_constraints_low = 1, 1
                    if curr_node.num is not None and curr_node.color:
                        priority_constraints_high = (new_node.num > curr_node.num)
                        priority_constraints_low = (new_node.num < curr_node.num)
                    # if curr_node.color is not None:
                        priority_constraints_high = priority_constraints_high and (new_node.color > curr_node.color)
                        priority_constraints_low = priority_constraints_low and (new_node.color < curr_node.color)
                    if p not in color_constraints:
                        check_equality_constraint = new_node.num == curr_node.num
                        # print(1, new_node.num, curr_node.num, check_equality_constraint)
                    else:
                        check_equality_constraint = new_node.num == curr_node.num or new_node.color == curr_node.color
                        # print(p)
                        # print(11, new_node.num, curr_node.num, check_equality_constraint)

                    if check_equality_constraint or not (priority_constraints_high or priority_constraints_low):
                        return False

                    if len(curr_node.domain) == 0:
                        # print('backtrack')
                        return False
        return True

    def calculate_degree(self, node):
        all_cons = self.constraint_of_nodes[node.loc]
        degree = 0
        num_cons = all_cons['numeric_constraints']
        color_cons = all_cons['color_constraints']
        for p in num_cons:
            # if p not in self.assigned_nodes:
            k = str(p[0] + 1) + str(p[1] + 1)
            if k in self.loc_assigned:
                degree += 1
                if p in color_cons:
                    degree += 1
        return degree

    def mrv_degree(self, csp):
        min_cons = float('inf')
        selected_node = None
        for r in csp.state:
            for p in r:
                # print(not p.is_assigned() == p.loc not in self.loc_assigned)
                # if p.is_assigned():
                # if p not in self.assigned_nodes:
                if p.loc not in self.loc_assigned:
                    num_of_valid_values = len(p.domain)
                    # print(p)
                    if num_of_valid_values < min_cons:
                        min_cons = num_of_valid_values
                        selected_node = p
                    elif num_of_valid_values == min_cons:
                        degree_node1 = self.calculate_degree(p)
                        degree_node2 = self.calculate_degree(selected_node)
                        if degree_node1 > degree_node2:
                            selected_node = p

        return selected_node

    def back_track_search(self, state):
        # dim = len(self.current_state.state)
        if len(self.assigned_nodes) == self.n ** 2:
            return self.assigned_nodes

        selected_node = self.mrv_degree(self.current_state)
        domain_copy = selected_node.domain

        for d in domain_copy:
            selected_before = self.used_domain[selected_node.loc]
            if (d[0], d[1]) not in selected_before:
                edited_node = Node(selected_node.loc, selected_node.num, selected_node.color, selected_node.domain)
                edited_node.num, edited_node.color = d[0], d[1]
                check_cons = self.check_consistency(state, edited_node)

                if check_cons:
                    self.current_state.replicate_state = deepcopy(self.current_state)
                    selected_node.num = d[0]
                    selected_node.color = d[1]
                    self.assigned_nodes.append(selected_node)
                    self.loc_assigned.append(selected_node.loc)
                    self.used_domain[selected_node.loc].append((d[0], d[1]))

                    not_empty_domain, self.current_state.replicate_state = \
                        self.forward_checking(self.current_state.replicate_state, selected_node)
                    if not_empty_domain:
                        selected_before.remove((d[0], d[1]))
                        res = self.back_track_search(self.current_state)
                        if res != 'fail':
                            return res
                    self.assigned_nodes.remove(selected_node)
                    self.loc_assigned.remove(selected_node.loc)
        return 'fail'
