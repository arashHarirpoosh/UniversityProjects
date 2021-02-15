from Project2.Model import *
from Project2.CSP import *
import numpy as np
import sys
import time


def print_result():
    key_color = list(color_map.keys())
    val_color = list(color_map.values())
    final_res = [[0 for x in range(n)] for y in range(n)]
    if res != 'fail':
        for r in res:
            final_res[int(r.loc[0]) - 1][int(r.loc[1]) - 1] = str(r.num) + key_color[val_color.index(r.color)]
        for r in final_res:
            print(r)
    else:
        print(res)


def combine_domains(num_domain1, color_domain1):
    domain = []
    for nd in num_domain1:
        for cd in color_domain1:
            domain.append((nd, cd))
    return domain


if __name__ == '__main__':
    info = input('Please Enter m, n: \n').split()
    m, n = int(info[0]), int(info[1])
    colors = input().split()
    highest_priority = len(colors)
    color_map = {colors[i]: highest_priority - i for i in range(highest_priority)}
    num_domain = [x for x in range(1, n+1)]
    color_domain = [v for k, v in color_map.items()]
    all_domain = combine_domains(num_domain, color_domain)
    # print(all_domain)
    initial_state_info = []
    for i in range(n):
        row = input().split()
        one_row = []
        for r in range(n):
            node_color = None
            num = None
            loc = str(i+1) + str(r+1)
            if row[r][0] != '*':
                num = int(row[r][0])
                if num > n:
                    print('Not Valid Number!!!')
                    break
            if row[r][1] != '#':
                node_color = color_map[row[r][1]]
            if num and node_color is not None:
                node_domain = [(num, node_color)]
            elif num is None and node_color is not None:
                node_domain = [(x, node_color) for x in num_domain]
            elif num is not None and node_color is None:
                node_domain = [(num, x) for x in color_domain]
            else:
                node_domain = all_domain.copy()

            node = Node(loc, num, node_color, np.array(node_domain))
            one_row.append(node)
        initial_state_info.append(one_row)
    initial_state = State(initial_state_info)
    start_time = time.time()
    csp = CSP(initial_state, m, n)
    csp.find_constraints_of_nodes()

    # Consistent The Domain Based On The Input Nodes
    for c in csp.current_state.state:
        for r in c:
            if r.num is not None or r.color is not None:
                csp.forward_checking(csp.current_state, r)
    # print(csp.constraint_of_nodes)
    sys.setrecursionlimit(100000000)
    print('Search Started....')
    res = csp.back_track_search(csp.current_state)
    end_time = time.time()
    print()
    print(f'Final State Has Found In {end_time - start_time} Seconds.')
    print_result()


