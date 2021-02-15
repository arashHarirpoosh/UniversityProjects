from Project1.IDS_TreeSearch import Search
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
    ids_search = Search(initial_state, m)
    res = ids_search.iterative_deepening_search(initial_depth=4)
    end_time = time.time()
    print()

    explored_nodes = ids_search.explored
    generated_nodes = ids_search.generate
    all_acts = ids_search.final_actions(res[1])
    depth = len(all_acts)
    ids_search.print_actions(all_acts, res[1])
    print()
    print(f'Goal Has Found In {end_time - start_time} Seconds.')
    print('Explored Nodes: ', explored_nodes)
    print('Generated Nodes: ', generated_nodes)
    print('Depth Search: ', depth)


