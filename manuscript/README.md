# Boundary formulas for Hardin's array recurrences and Barker's generating functions

The note establishes the empirical formulas in OEIS A233156, revision 8
(9 October 2018), both formulas in A233157, revision 8 (9 October 2018),
and every displayed row and column recurrence in A233155, revision 6
(3 September 2022). The coefficient lists for rows five through seven are
the formulas in A233158, A233159 and A233160, revision 4 (5 December 2013).
All arrays are labeled. Horizontal and antidiagonal neighbors, but not
vertical neighbors, must avoid summing to two.

For three rows and width `n >= 3`, the array count is exactly 36 times
the proper three-coloring count of the ordinary `3 by (n-2)` rectangular
grid. Thus the three-row formulas follow from Biggs and Meredith's
double-strip enumeration (1976, Section 3, Theorem 2, pp. 10–11):
https://doi.org/10.1016/0095-8956(76)90062-9
An author-hosted copy is listed at https://normanbiggs.com/research-papers-to-1988.

Later grid-count derivations appear in Roček–Shrock–Tsai (preprint 1997,
Section II.B), Salas–Sokal (preprint 2000, Section 5.2), Ginepro–Hull
(2014, Section 3 and Theorem 4), and Spahn (2024, Section 6.1).
The note gives the complete boundary reduction and a direct five-state
proof; it treats the three-row result as a consequence of this older
enumeration, not a claim of priority. For the larger strips it separates
the classical denominator formulas from the full array numerators,
exceptional initial terms and recurrence ranges.

## Contents

- `note.tex`: self-contained LaTeX with bibliography; `note.pdf` is distributed separately.
- `verify.py` and `verification.json`: exact finite checks for the three-row proof and thin strips.
- `siblings.py` and `siblings-verification.json`: exact finite checks for the remaining recurrences.
- `certificates.json`: equality-pattern matrices and all continuation vectors needed for their identities.
- `boundary.py` and `boundary-verification.json`: exact boundary-extension counts and grid comparisons.
- `metadata.json`: authors, license, mathematical coverage and scientific source links.
- `LICENSE`: CC BY 4.0 notice.

## Build

Use Tectonic 0.17.0:

```sh
tectonic note.tex
```

Or use a standard LaTeX distribution:

```sh
pdflatex -interaction=nonstopmode -halt-on-error note.tex
pdflatex -interaction=nonstopmode -halt-on-error note.tex
```

The bibliography is part of `note.tex`; no separate BibTeX database is needed.

## Exact finite identities

Use Python 3.10 or later; no third-party Python packages are needed.

```sh
python3 verify.py > verification-new.json
diff -u verification.json verification-new.json
python3 siblings.py > siblings-verification-new.json
diff -u siblings-verification.json siblings-verification-new.json
python3 boundary.py > boundary-verification-new.json
diff -u boundary-verification.json boundary-verification-new.json
```

The first checker reconstructs every three-entry column quotient row,
checks the continuation identity, compares literal and five-state counts
through width 210, and directly enumerates arrays through width four.
It also checks the thin-strip formulas on the ranges in its output.

The second checker constructs column-pattern matrices of dimensions
5, 14, 41, 122 and 365 and proper-row matrices of dimensions 8, 16 and 32.
It checks each entry and continuation vector against `certificates.json`,
then verifies the exact zero-vector polynomial relations in the note.
Literal sum-exclusion counts for heights 1 through 7 and widths 1 through
72 are a separate finite comparison. The column-six recurrence starts at
height four; its first instance is checked separately from the vector relation.

The boundary checker enumerates every proper three-entry core boundary
with two through five colors and confirms the exact extension factor
`(q-1)(q*q-3*q+3)` at each end. It compares the full sheared-graph and
rectangular-grid counts through width ten for those color sets, and
through width 72 for three colors. It also checks the Biggs–Meredith
matrix relation and the cited Roček–Shrock–Tsai denominator
specializations. The all-width chromatic-polynomial identity has a
written graph-decomposition proof, separate from these finite checks.

The all-length conclusions follow from the written counting induction
and the specified finite integer identities, rather than a prefix match.
Only the three-row recurrence is described by the linked formal statement:

https://github.com/the-omega-institute/trureturing/blob/e135d8e2afafffb707a541357df302c35e90baff/D5/S3/Combinatorics/TraceAvoidingArrays/HardinA233156Row.lean

`HardinA233156Row.result` states the recurrence for every natural shift,
using the literal three-color array count. Its counting bridge uses
`properEquiv` in the following file for the alternating-column bijection:

https://github.com/the-omega-institute/trureturing/blob/e135d8e2afafffb707a541357df302c35e90baff/D5/S3/Combinatorics/TraceAvoidingArrays/HardinA233155ColumnTransfer.lean

The five-state count for widths at least two is `count_transfer` in:

https://github.com/the-omega-institute/trureturing/blob/e135d8e2afafffb707a541357df302c35e90baff/D5/S3/Combinatorics/TraceAvoidingArrays/HardinA233258PairTransfer.lean

Here the last file's definitions are three-color definitions, unrelated
to the six-color OEIS problem suggested by its filename. The generating
functions, three-row minimality and closed form have written proofs.
The additional row and column recurrences use the finite identities and
written deductions in the corollary on the remaining parent-table
recurrences; they are not assigned further formal scope. The rectangular
boundary reduction also has a written proof and finite-check coverage.

## Authors and license

Haobo Ma — ChronoAI Pte Ltd, Singapore.

Wenlin Zhang — National University of Singapore; ChronoAI Pte Ltd, Singapore.

Copyright 2026 Haobo Ma and Wenlin Zhang. CC BY 4.0 (`cc-by-4.0`).
https://creativecommons.org/licenses/by/4.0/
