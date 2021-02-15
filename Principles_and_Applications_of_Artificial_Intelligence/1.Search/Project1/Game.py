from copy import deepcopy


def card_choices(row_num, state):
    node = state[row_num]
    selected_card = node[len(node) - 1]
    part_actions = []
    for i in range(len(state)):
        this_state = state[i]
        if len(this_state) > 0:
            last_card = this_state[len(this_state) - 1]
            if state[i] != node:
                if selected_card[0] < last_card[0]:
                    part_actions.append((row_num, i))

        else:
            part_actions.append((row_num, i))

    return part_actions


def actions(state):
    all_actions = []
    for i in range(len(state)):
        if len(state[i]) > 0:
            possible_actions = card_choices(i, state)
            for p in possible_actions:
                all_actions.append(p)

    return all_actions


def do_action(state, i, j):
    child = deepcopy(state)
    card = child[i].pop()
    child[j].append(card)
    return child


def check_color(s):
    last_color = s[0][1]
    for i in range(1, len(s)):
        if s[i][1] != last_color:
            return False
    return True


def check_order(s):
    last_num = s[0][0]
    for i in range(1, len(s)):
        if last_num <= s[i][0]:
            return False
        last_num = s[i][0]
    return True


def goal_test(state, m):
    not_empty = 0
    for s in state:
        size = len(s)
        if 0 < size:
            not_empty += 1
            if not (check_color(s) and check_order(s)):
                return False
    if not_empty != m:
        return False

    return True
