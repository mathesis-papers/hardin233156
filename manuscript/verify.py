import argparse
import hashlib
from itertools import product
import json
from pathlib import Path


COLORS = range(3)
COLUMNS = tuple(product(COLORS, repeat=3))
REPRESENTATIVES = ((0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 1, 2))
MATRIX = ((2, 2, 2, 2, 0), (1, 1, 0, 1, 1), (1, 1, 0, 0, 0),
          (1, 1, 1, 1, 0), (0, 0, 0, 1, 1))
MULTIPLICITIES = (3, 6, 6, 6, 6)
SOURCE_PREFIX = (27, 96, 432, 1944, 8856, 40392, 184248, 840456, 3833784,
                 17488008, 79772472, 363886344, 1659886776, 7571661192,
                 34538532408, 157549339656, 718669633464, 3278249488008,
                 14953908173112, 68213041889544, 311157393101496)


def column_class(column):
    first, second, third = column
    if first == second:
        return 0 if first == third else 1
    if first == third:
        return 2
    return 3 if second == third else 4


def literal_compatible(left, right):
    return (all(left[row] + right[row] != 2 for row in range(len(left)))
            and all(left[row + 1] + right[row] != 2
                    for row in range(len(left) - 1)))


def proper_compatible(left, right):
    return (all(left[row] != right[row] for row in range(len(left)))
            and all(left[row + 1] != right[row] for row in range(len(left) - 1)))


def matrix_vector(matrix, vector):
    return tuple(sum(entry * value for entry, value in zip(row, vector)) for row in matrix)


def dot(left, right):
    return sum(first * second for first, second in zip(left, right))


def literal_counts(height, limit):
    columns = tuple(product(COLORS, repeat=height))
    predecessors = tuple(tuple(index for index, left in enumerate(columns)
                               if literal_compatible(left, right)) for right in columns)
    counts = [1] * len(columns)
    totals = [1, sum(counts)]
    for length in range(2, limit + 1):
        counts = [sum(counts[index] for index in indices) for indices in predecessors]
        totals.append(sum(counts))
    return totals


def direct_array_count(length):
    edges = tuple((row * length + column, row * length + column + 1)
                  for row in range(3) for column in range(length - 1))
    edges += tuple(((row + 1) * length + column, row * length + column + 1)
                   for row in range(2) for column in range(length - 1))
    return sum(all(array[first] + array[second] != 2 for first, second in edges)
               for array in product(COLORS, repeat=3 * length))


def check(bfile=None):
    for left in COLUMNS:
        for right in COLUMNS:
            complement = tuple(2 - value for value in right)
            assert literal_compatible(left, right) == proper_compatible(left, complement)
    assert tuple(sum(column_class(column) == index for column in COLUMNS)
                 for index in range(5)) == MULTIPLICITIES
    for left in COLUMNS:
        observed = tuple(sum(proper_compatible(left, right) and column_class(right) == index
                             for right in COLUMNS) for index in range(5))
        assert observed == MATRIX[column_class(left)]
    vectors = [(1,) * 5]
    for exponent in range(4):
        vectors.append(matrix_vector(MATRIX, vectors[-1]))
    assert vectors == [(1, 1, 1, 1, 1), (8, 4, 2, 4, 2), (36, 18, 12, 18, 6),
                       (168, 78, 54, 84, 24), (768, 354, 246, 384, 108)]
    residual = tuple(vectors[4][index] - 5 * vectors[3][index]
                     + 2 * vectors[2][index] for index in range(5))
    assert residual == (0,) * 5
    literal = literal_counts(3, 210)
    vector = (1,) * 5
    orbit = [1]
    for length in range(1, 211):
        orbit.append(dot(MULTIPLICITIES, vector))
        vector = matrix_vector(MATRIX, vector)
    assert literal == orbit
    assert tuple(literal[1:22]) == SOURCE_PREFIX
    direct = [direct_array_count(length) for length in range(5)]
    assert direct == literal[:5] == [1, 27, 96, 432, 1944]
    assert all(literal[length] == 5 * literal[length - 1] - 2 * literal[length - 2]
               for length in range(5, 211))
    assert literal[4] - 5 * literal[3] + 2 * literal[2] == -24
    assert all(literal[length] * literal[length + 2] - literal[length + 1] ** 2
               == 46656 * 2 ** (length - 3) for length in range(3, 209))
    positive_series = [0] + literal[1:]
    numerator = [positive_series[length]
                 - (5 * positive_series[length - 1] if length >= 1 else 0)
                 + (2 * positive_series[length - 2] if length >= 2 else 0)
                 for length in range(211)]
    assert numerator[:5] == [0, 27, -39, 6, -24]
    assert all(value == 0 for value in numerator[5:])
    first_row = literal_counts(1, 12)
    second_row = literal_counts(2, 12)
    assert all(first_row[length] == 3 * 2 ** (length - 1) for length in range(1, 13))
    assert second_row[1] == 9
    assert all(second_row[length] == 24 * 3 ** (length - 2) for length in range(2, 13))
    row_representatives = ((0, 1, 0, 1), (0, 1, 0, 2), (0, 1, 2, 0), (0, 1, 2, 1))
    proper_rows = tuple(row for row in product(COLORS, repeat=4)
                        if all(row[index] != row[index + 1] for index in range(3)))
    row_matrix = ((3, 3, 2, 2), (2, 2, 2, 2), (2, 2, 2, 2), (3, 3, 2, 2))
    def row_pattern(row):
        colors = tuple(dict.fromkeys(row))
        return tuple(colors.index(value) for value in row)
    for top in proper_rows:
        observed = tuple(sum(row_pattern(bottom) == target
                             and all(bottom[index] != top[index + 1] for index in range(3))
                             for bottom in proper_rows) for target in row_representatives)
        assert observed == row_matrix[row_representatives.index(row_pattern(top))]
    row_vector = matrix_vector(row_matrix, (1,) * 4)
    assert row_vector == (10, 8, 8, 10)
    assert matrix_vector(row_matrix, row_vector) == tuple(9 * value for value in row_vector)
    for height in range(1, 7):
        counts = literal_counts(height, 4)
        assert counts[1] == 3 ** height
        assert counts[2] == 6 * 4 ** (height - 1)
        assert counts[3] == 12 * 6 ** (height - 1)
        assert counts[4] == 24 * 9 ** (height - 1)
    result = {
        'status': 'pass',
        'arithmetic': 'exact integers',
        'column_pairs': 729,
        'alternating_complement_pairs': 729,
        'quotient_fibres': 135,
        'matrix': MATRIX,
        'multiplicities': MULTIPLICITIES,
        'continuation_vectors': vectors,
        'matrix_identity_residual': residual,
        'literal_and_orbit_count_range': [1, 210],
        'direct_array_count_range': [0, 4],
        'direct_array_counts': direct,
        'source_prefix_terms': 21,
        'recurrence_range': [5, 210],
        'recurrence_residual_at_four': -24,
        'minimality_determinant_range': [3, 208],
        'minimality_determinant_initial': 46656,
        'positive_series_numerator': numerator[:5],
        'thin_rows_checked': {'height': [1, 2], 'length': [1, 12]},
        'thin_columns_checked': {'height': [1, 6], 'length': [1, 4]},
        'four_column_row_matrix': row_matrix,
        'four_column_proper_row_pairs': 576,
        'scope': 'Finite counts and exact matrix identities; the note supplies the all-length proof.',
    }
    if bfile is not None:
        rows = []
        for line in bfile.read_text().splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                index, value = map(int, stripped.split())
                rows.append((index, value))
        assert [index for index, value in rows] == list(range(1, 211))
        assert all(literal[index] == value for index, value in rows)
        result['oeis_bfile_comparison'] = {
            'range': [1, 210],
            'sha256': hashlib.sha256(bfile.read_bytes()).hexdigest(),
        }
    return result


def main():
    parser = argparse.ArgumentParser(description='Exact checks for the three-row array formulas.')
    parser.add_argument('--bfile', type=Path)
    arguments = parser.parse_args()
    print(json.dumps(check(arguments.bfile), indent=2) + '\n', end='')


if __name__ == '__main__':
    main()
