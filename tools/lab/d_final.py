"""The data charts after the second 11-17 cycle (d1.py, d2.py, d3.py): FINAL = {name: function(W)}.

opd-compute stopped after round 2 (its round-3 entry is the round-2 merge) and opd-methods only got a phone fix in round
3; the other six are round 3's merges. tools/figures.py can take these instead of c_final.FINAL; the pages show the English text only.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
for _p in (str(HERE.parent), str(HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import d3  # noqa: E402

FINAL = dict(d3.MERGED)
