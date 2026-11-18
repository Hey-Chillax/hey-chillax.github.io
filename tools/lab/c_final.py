"""Final versions of the eight data charts after the 11-17 cycle (rounds c1, c2, c3; see c_rounds.py).

    from c_final import FINAL      # name -> function(W) returning a figlib Svg (W = 720 desktop, 360 phone)
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
for p in (str(HERE.parent), str(HERE), str(HERE / 'v2')):
    if p not in sys.path:
        sys.path.insert(0, p)

import c3  # noqa: E402

FINAL = dict(c3.MERGED)
