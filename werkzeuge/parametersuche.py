"""Beste Antwort gegen ein Feld aus Faustregel-Spielern: alle Parameter-Kombinationen für Spieler 0.

python werkzeuge/parametersuche.py --spieler 3 --spiele 50000 --finale 2000000
"""

import argparse
import itertools
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from schocken.schnell import FAUSTREGEL, verlustquoten  # noqa: E402

GITTER = {
    "starter_klasse": range(6),
    "verdeckt_wurf": range(4),
    "folger_klasse": range(6),
    "folger_marge": (0, 100, 200, 1000),
    "drehen": (0, 1),
}


def bewerte(kandidat, spieler, spiele, seed):
    params = np.tile(FAUSTREGEL, (spieler, 1))
    params[0] = kandidat
    q, f = verlustquoten(params, spiele, seed)
    return q[0], f[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spieler", type=int, default=3)
    ap.add_argument("--spiele", type=int, default=50_000)
    ap.add_argument("--finale", type=int, default=2_000_000)
    ap.add_argument("--top", type=int, default=15)
    args = ap.parse_args()

    kandidaten = list(itertools.product(*GITTER.values()))
    t = time.time()
    grob = []
    for i, k in enumerate(kandidaten):
        q, _ = bewerte(k, args.spieler, args.spiele, seed=i)
        grob.append((q, k))
    grob.sort()
    print(f"{len(kandidaten)} Kandidaten x {args.spiele} Spiele in {time.time() - t:.0f}s")

    basis, basis_f = bewerte(FAUSTREGEL, args.spieler, args.finale, seed=999)
    print(f"\n{args.spieler} Spieler. Faire Quote: {1 / args.spieler:.4f}. "
          f"Faustregel gegen Faustregel: {basis:.4f} +- {basis_f:.4f}")
    print(f"\nTop {args.top} (nachgemessen mit {args.finale} Spielen), Parameter = {list(GITTER)}:")
    fein = []
    for _, k in grob[: args.top]:
        q, f = bewerte(k, args.spieler, args.finale, seed=12345)
        fein.append((q, f, k))
    for q, f, k in sorted(fein):
        print(f"  {k}: Verlustquote {q:.4f} +- {f:.4f}")
    print("\nSchlechteste 5 (grob):")
    for q, k in grob[-5:]:
        print(f"  {k}: {q:.4f}")


if __name__ == "__main__":
    main()
