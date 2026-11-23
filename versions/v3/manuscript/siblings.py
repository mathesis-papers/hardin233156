import argparse
from itertools import product
import json
from pathlib import Path


ROW_RECURRENCES = {
    3: (5, (5, -2)),
    4: (8, (9, -15, 6)),
    5: (12, (16, -64, 76, 17, -84, 48, -8)),
    6: (16, (30, -283, 1038, -573, -6705, 21056, -27636, 17216, -4128)),
    7: (34, (55, -1066, 8965, -19778, -225541, 2020719, -6851286,
             7381301, 20655503, -79401996, 80882723, 65337447, -222811374,
             135953338, 120111164, -197698384, 43440564, 76879396, -52839536,
             -1810608, 13170096, -4166800, -433792, 532928, -126464, 13056, -512)),
}
COLUMN_RECURRENCES = {5: (15, -18), 6: (25, -90, 81), 7: (42, -351, 972, -810)}


def canonical(values):
    labels = {}
    return tuple(labels.setdefault(value, len(labels)) for value in values)


def dot(left, right):
    return sum(first * second for first, second in zip(left, right))


def multiply(matrix, vector):
    return tuple(dot(row, vector) for row in matrix)


def column_matrix(height):
    representatives = sorted({canonical(column) for column in product(range(3), repeat=height)})
    indices = {column: index for index, column in enumerate(representatives)}
    matrix = []
    for left in representatives:
        choices = [tuple(color for color in range(3) if color != left[index]
                         and (index + 1 == height or color != left[index + 1]))
                   for index in range(height)]
        row = [0] * len(representatives)
        for right in product(*choices):
            row[indices[canonical(right)]] += 1
        matrix.append(tuple(row))
    weights = tuple(3 if len(set(column)) == 1 else 6 for column in representatives)
    return representatives, tuple(matrix), weights


def row_matrix(width):
    rows = tuple(row for row in product(range(3), repeat=width)
                 if all(row[index] != row[index + 1] for index in range(width - 1)))
    representatives = sorted({canonical(row) for row in rows})
    indices = {row: index for index, row in enumerate(representatives)}
    matrix = []
    for top in representatives:
        result = [0] * len(representatives)
        for bottom in rows:
            if all(bottom[index] != top[index + 1] for index in range(width - 1)):
                result[indices[canonical(bottom)]] += 1
        matrix.append(tuple(result))
    return representatives, tuple(matrix), (6,) * len(representatives)


def make_certificate(axis, size, coefficients, shift):
    representatives, matrix, weights = (column_matrix(size) if axis == 'row' else row_matrix(size))
    degree = len(coefficients)
    vectors = [(1,) * len(matrix)]
    for exponent in range(degree + shift):
        vectors.append(multiply(matrix, vectors[-1]))
    residual = tuple(vectors[degree + shift][index] - sum(
        coefficient * vectors[degree + shift - lag][index]
        for lag, coefficient in enumerate(coefficients, 1)) for index in range(len(matrix)))
    assert not any(residual)
    return {'axis': axis, 'size': size, 'representatives': representatives,
            'matrix': matrix, 'weights': weights, 'coefficients': coefficients,
            'shift': shift, 'vectors': vectors, 'residual': residual}


def literal_counts(height, limit):
    columns = tuple(product(range(3), repeat=height))
    indices = {column: index for index, column in enumerate(columns)}
    successors = []
    for left in columns:
        choices = [tuple(color for color in range(3) if left[index] + color != 2
                         and (index + 1 == height or left[index + 1] + color != 2))
                   for index in range(height)]
        successors.append(tuple(indices[right] for right in product(*choices)))
    counts = (1,) * len(columns)
    totals = []
    for length in range(1, limit + 1):
        totals.append(sum(counts))
        counts = tuple(sum(counts[index] for index in targets) for targets in successors)
    return totals


def check(certificate_path, write=False):
    certificates = [make_certificate('row', height, coefficients, onset - 1 - len(coefficients))
                    for height, (onset, coefficients) in ROW_RECURRENCES.items()]
    certificates.extend(make_certificate('column', width, coefficients, int(width == 6))
                        for width, coefficients in COLUMN_RECURRENCES.items())
    serialized = json.loads(json.dumps(certificates))
    if write:
        certificate_path.write_text(json.dumps(serialized, separators=(',', ':')) + '\n')
    assert json.loads(certificate_path.read_text()) == serialized
    summaries = []
    literal = {height: literal_counts(height, 72) for height in range(1, 8)}
    for certificate in certificates:
        matrix, weights = certificate['matrix'], certificate['weights']
        vector = (1,) * len(matrix)
        counts = []
        for length in range(1, 73):
            counts.append(dot(weights, vector))
            vector = multiply(matrix, vector)
        axis, size = certificate['axis'], certificate['size']
        if axis == 'row':
            assert counts == literal[size]
            onset = ROW_RECURRENCES[size][0]
        else:
            assert counts[:7] == [literal[height][size - 1] for height in range(1, 8)]
            onset = len(certificate['coefficients']) + 1
        coefficients = certificate['coefficients']
        assert all(counts[length - 1] == sum(coefficient * counts[length - lag - 1]
                   for lag, coefficient in enumerate(coefficients, 1))
                   for length in range(onset, 73))
        summaries.append({'axis': axis, 'size': size, 'dimension': len(matrix),
                          'degree': len(coefficients), 'shift': certificate['shift'],
                          'zero_vector_identity': True, 'recurrence_checked': [onset, 72],
                          'initial_values': counts[:onset - 1]})
    four_row = literal[4]
    numerator = [0] + [four_row[index - 1]
        - (9 * four_row[index - 2] if index > 1 else 0)
        + (15 * four_row[index - 3] if index > 2 else 0)
        - (6 * four_row[index - 4] if index > 3 else 0) for index in range(1, 73)]
    assert numerator[:8] == [0, 81, -345, 351, -558, 288, -1080, 648]
    assert not any(numerator[8:])
    assert four_row[6] - 9 * four_row[5] + 15 * four_row[4] - 6 * four_row[3] == 648
    return {'status': 'pass', 'arithmetic': 'exact integers', 'certificates': summaries,
            'literal_sum_exclusion_counts': {'heights': [1, 7], 'widths': [1, 72]},
            'column_counts_compared_with_literal_arrays': {'heights': [1, 7], 'widths': [5, 7]},
            'four_row_generating_numerator': numerator[:8],
            'four_row_recurrence_residual_at_seven': 648,
            'six_column_recurrence_at_height_four': True,
            'scope': 'Exact finite matrix identities with all-length deductions in the note.'}


def main():
    parser = argparse.ArgumentParser(description='Exact finite identities for the displayed array recurrences.')
    parser.add_argument('--certificates', type=Path, default=Path(__file__).with_name('certificates.json'))
    parser.add_argument('--write-certificates', action='store_true')
    arguments = parser.parse_args()
    print(json.dumps(check(arguments.certificates, arguments.write_certificates), indent=2))


if __name__ == '__main__':
    main()
