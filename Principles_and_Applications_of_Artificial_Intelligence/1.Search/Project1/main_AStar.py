from Project1.AStar_GraphSearch import Search
import time


if __name__ == '__main__':
    info = input('Please Enter n, m, k: \n').split()
    n, m, k = int(info[0]), int(info[1]), int(info[2])
    initial_state = []
    for i in range(k):
        row = input().split()
        if row[0] == '#':
            row = []
        new_rows = []
        for r in row:
            num = int(r[0])
            if num <= n:
                new_rows.append((num, r[1]))
            else:
                print('Not Valid Card Number!!!')
                break
        initial_state.append(new_rows)

    print('Processing The Input.....')
    start_time = time.time()
    a_star_search = Search(initial_state, m, n)
    res = a_star_search.AStar_GraphSearch()
    end_time = time.time()
    print()

    explored_nodes = len(a_star_search.explored)
    front_node = len(a_star_search.frontier)
    all_acts = a_star_search.final_actions(res)
    depth = len(all_acts)
    a_star_search.print_actions(all_acts, res)
    print()
    print(f'Goal Has Found In {end_time - start_time} Seconds.')
    print('Explored Nodes: ', explored_nodes)
    print('Generated Nodes: ', explored_nodes+front_node)
    print('Depth Search: ', depth)


