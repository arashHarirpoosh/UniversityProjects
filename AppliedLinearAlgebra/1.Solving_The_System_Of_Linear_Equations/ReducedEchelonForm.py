import numpy as np
import math


# Interchange The Row i with Row j
def interchange_rows(matrix, i, j):
    # Swap The Rows
    matrix[[i, j]] = matrix[[j, i]]


def make_num_valid(num):
    if math.ceil(num) - num < 0.00000000001:
        return math.ceil(num)
    elif num - math.floor(num) < 0.00000000001:
        return math.floor(num)
    else:
        return num


# Row Replacement
def row_replacement(matrix, i, j, forward):
    dim = matrix.shape[0]

    # Forward Row Replacement
    if forward:
        r = range(i+1, dim)

    # Backward Row Replacement
    else:
        r = range(i-1, -1, -1)

    for p in r:
        element = matrix[p][j]
        if element != 0:
            coefficient = -(element / matrix[i][j])

            matrix[p] += coefficient * matrix[i]
            temp = [make_num_valid(x) for x in matrix[p]]
            matrix[p] = temp


# Forward Step
def convert_to_echelon_form(matrix):
    dim = matrix.shape
    pivot_columns = []

    for k in range(dim[0]):
        pivot = None
        for j in range(k, dim[1]):
            for i in range(k, dim[0]):
                if matrix[i][j] != 0:
                    pivot = (i, j, k)
                    pivot_columns.append(j)
                    break
            if pivot is not None:
                break
        if pivot is not None:

            if matrix[k][pivot[1]] == 0:
                interchange_rows(matrix, pivot[0], pivot[1])

            row_replacement(matrix, k, pivot[1], True)
    return pivot_columns


# Backward Step
def convert_to_reduced_echelon_form(echelon_form_matrix):
    dim = echelon_form_matrix.shape

    for i in range(dim[0]-1, -1, -1):
        for j in range(dim[1]-1):
            if echelon_form_matrix[i][j] != 0:
                echelon_form_matrix[i] *= 1 / echelon_form_matrix[i][j]
                row_replacement(echelon_form_matrix, i, j, False)
                break


# Calculate The Basic Variables And Detect Free Ones
def result(matrix, all_pivot_column):
    dim = matrix.shape
    res = {}
    for i in range(dim[0]):
        if np.count_nonzero(matrix[i][:dim[1]-1] == 0) == dim[1]-1 and matrix[i][dim[1]-1] != 0:
            res['Err'] = 'This Equation System Has No Answer!!!'
            return False, res

    # Discover Free Variables
    for i in range(dim[1]-1):
        if i not in all_pivot_column:
            res['X'+str(i+1)] = 'X' + str(i+1) + ' Is Free Variable.'

    # Calculate Basic Variables
    for i in range(dim[0]):
        c = None
        for j in range(dim[1]):
            if matrix[i][j] != 0:
                c = j
                break
        if c is not None:
            temp = 'X'+str(c+1) + ': '
            for k in range(c+1, dim[1]-1):
                if matrix[i][k] != 0:
                    temp += '('+str(-matrix[i][k]) + ' * X'+str(k+1)+')' + ' + '
            temp += '('+str(matrix[i][dim[1]-1])+')'
            res['X'+str(c+1)] = temp

    return True, res


if __name__ == '__main__':
    print('Coefficient Matrix: ')
    dim = input('Enter Number Of Rows And Columns Respectively:\n').split(' ')
    coefficient_matrix = []
    # Create Coefficient Matrix
    for i in range(1, int(dim[0])+1):
        row = input('Enter row ' + str(i) + ':\n').split(' ')
        coefficient_matrix.append([float(x) for x in row])

    const_values = input('Enter Constant Values:\n').split(' ')

    # Convert Coefficient Matrix to Augmented Matrix
    for i in range(0, int(dim[0])):
        coefficient_matrix[i].append(float(const_values[i]))

    augmented_matrix = np.array(coefficient_matrix, dtype=np.float64)
    print('Given Matrix: \n', augmented_matrix)

    final_pivot_columns = convert_to_echelon_form(augmented_matrix)

    print('\nEchelon Form Of Matrix: \n', augmented_matrix)

    convert_to_reduced_echelon_form(augmented_matrix)
    print('\nReduced Echelon Form Of Matrix: \n', augmented_matrix)


    final_res = result(augmented_matrix, final_pivot_columns)
    if final_res[0]:
        print('\nAnswer Of This Equation System Equals To: ')
        for x in range(len(final_res[1])):
            print(final_res[1]['X' + str(x + 1)])
    else:
        print(final_res[1]['Err'])

