from plugin import plugin
from colorama import Fore


def get_matrix(ally, r, c):
    matrix = []
    for i in range(r):
        row_str = ally.input("enter row #{:d}: ".format(i))
        cur_row = []
        for n in row_str.split():
            try:
                int(n)
            except ValueError:
                cur_row.append(0)
            else:
                cur_row.append(int(n))
        while len(cur_row) != c:
            ally.say("Row length should be {:d}".format(c))
            row_str = ally.input("enter row #{:d}: ".format(i))

            for n in row_str.split():
                try:
                    int(n)
                except ValueError:
                    cur_row.append(0)
                else:
                    cur_row.append(int(n))
        matrix.append(cur_row)
    return matrix


def print_matrix(matrix, r, c):
    for i in range(r):
        print(matrix[i])


@plugin("matrix add")
def matrix_add(ally, s):
    ally.say("Sum of matrices with dimensions M x N", Fore.GREEN)

    row = int(ally.input_number('Enter M (rows): '))
    col = int(ally.input_number('Enter N (cols): '))

    initial = get_matrix(ally, row, col)

    while True:
        next_decision = ally.input("Continue with next matrix? ")
        if next_decision.lower() == 'no':
            break
        next_matrix = get_matrix(ally, row, col)
        for i in range(row):
            for j in range(col):
                initial[i][j] += next_matrix[i][j]
        current_decision = ally.input("Print current sum matrix? ")
        if current_decision.lower() != 'no':
            print_matrix(initial, row, col)

    ally.say('Final sum matrix:')
    print_matrix(initial, row, col)
