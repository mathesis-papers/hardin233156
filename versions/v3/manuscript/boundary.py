from itertools import product
import json


def advance_counts(columns, successors, length):
    counts = [1] * len(columns)
    totals = []
    for width in range(1, length + 1):
        totals.append(sum(counts))
        counts = [sum(counts[target] for target in adjacent) for adjacent in successors]
    return totals


def grid_counts(colors, length):
    columns = [column for column in product(range(colors), repeat=3)
               if column[0] != column[1] and column[1] != column[2]]
    successors = [[index for index, right in enumerate(columns)
                   if all(left[row] != right[row] for row in range(3))] for left in columns]
    return advance_counts(columns, successors, length)


def sheared_counts(colors, length):
    columns = list(product(range(colors), repeat=3))
    successors = [[index for index, right in enumerate(columns)
                   if all(left[row] != right[row] for row in range(3))
                   and all(left[row + 1] != right[row] for row in range(2))]
                  for left in columns]
    return advance_counts(columns, successors, length)


def boundary_extensions(column, colors, right=False):
    count = 0
    for first, second, pendant in product(range(colors), repeat=3):
        if right:
            allowed = (first != column[1] and second != column[2]
                       and first != second and pendant != second)
        else:
            allowed = (first != column[0] and second != column[1]
                       and first != second and pendant != first)
        count += allowed
    return count


def matrix_multiply(left, right):
    return [[sum(first * second for first, second in zip(row, column))
             for column in zip(*right)] for row in left]


def specialize(coefficients, value=3):
    result = 0
    for coefficient in coefficients:
        result = result * value + coefficient
    return result


def check():
    boundary_results = []
    for colors in range(2, 6):
        expected = (colors - 1) * (colors * colors - 3 * colors + 3)
        columns = [column for column in product(range(colors), repeat=3)
                   if column[0] != column[1] and column[1] != column[2]]
        for column in columns:
            assert boundary_extensions(column, colors) == expected
            assert boundary_extensions(column, colors, right=True) == expected
        grid = grid_counts(colors, 8)
        sheared = sheared_counts(colors, 10)
        assert sheared[2:] == [expected * expected * count for count in grid]
        boundary_results.append({'colors': colors, 'proper_boundary_columns': len(columns),
                                 'extensions_per_end': expected,
                                 'array_widths_compared': [3, 10]})
    transfer = [[4, 1], [2, 1]]
    squared = matrix_multiply(transfer, transfer)
    residual = [[squared[row][column] - 5 * transfer[row][column]
                 + 2 * int(row == column) for column in range(2)] for row in range(2)]
    assert residual == [[0, 0], [0, 0]]
    grid = grid_counts(3, 70)
    arrays = sheared_counts(3, 72)
    assert arrays[2:] == [36 * count for count in grid]
    assert grid[:3] == [12, 54, 246]
    assert all(grid[index] == 5 * grid[index - 1] - 2 * grid[index - 2]
               for index in range(2, len(grid)))
    grid_numerator = [grid[0], grid[1] - 5 * grid[0]]
    assert grid_numerator == [12, -6]
    related_one = [2, 9]
    related_two = [1, 4]
    for index in range(2, 72):
        related_one.append(5 * related_one[-1] - 2 * related_one[-2])
        related_two.append(5 * related_two[-1] - 2 * related_two[-2])
    assert arrays[2:] == [216 * related_one[index] for index in range(70)]
    assert arrays[2:] == [108 * related_two[index + 1] for index in range(70)]
    numerator = [arrays[index] - (5 * arrays[index - 1] if index else 0)
                 + (2 * arrays[index - 2] if index > 1 else 0)
                 for index in range(len(arrays))]
    assert numerator[:4] == [27, -39, 6, -24] and not any(numerator[4:])
    strip_three = [specialize([-1, 5, -11, 10]),
                   2 * specialize([1, -6, 13, -11])]
    assert strip_three == [-5, 2]
    strip_four = [specialize([-1, 7, -23, 41, -33]),
                  specialize([2, -23, 116, -329, 553, -517, 207]),
                  specialize([-1, 16, -112, 449, -1130, 1829, -1858, 1084, -279])]
    assert strip_four == [-9, 15, -6]
    diagonal_three = [specialize([-1, 8, -28, 53, -56, 27]), 2 * 1 * 3 ** 2]
    diagonal_four = [specialize([-1, 10, -45, 116, -185, 178, -82]),
                     3 ** 2 * specialize([3, -22, 64, -88, 49]), -3 ** 4]
    assert diagonal_three == [-15, 18]
    assert diagonal_four == [-25, 90, -81]
    return {'status': 'pass', 'arithmetic': 'exact integers',
            'boundary_extension_checks': boundary_results,
            'three_color_array_grid_identity': {'factor': 36, 'array_widths': [3, 72],
                                                 'grid_widths': [1, 70]},
            'Biggs_Meredith_matrix': transfer, 'matrix_polynomial_residual': residual,
            'three_row_grid_initial_values': grid[:3],
            'three_row_grid_generating_numerator': grid_numerator,
            'OEIS_sequence_identities': {'A020698_factor': 216, 'A020698_shift': -3,
                                         'A052913_factor': 108, 'A052913_shift': -2,
                                         'array_widths_compared': [3, 72]},
            'array_generating_numerator_degrees_1_to_4': numerator[:4],
            'Rocek_Shrock_Tsai_denominators_at_three_colors': {
                'square_three_rows': [1] + strip_three,
                'square_four_rows': [1] + strip_four,
                'diagonal_three': [1] + diagonal_three,
                'diagonal_four': [1] + diagonal_four},
            'scope': 'Boundary counts and finite comparisons; the all-width boundary decomposition is proved in the note.'}


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
