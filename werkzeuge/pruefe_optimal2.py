"""Prüft die exakte 2-Spieler-Lösung per Simulation in der Referenz-Engine.

python werkzeuge/pruefe_optimal2.py --spiele 5000
"""

import argparse
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from schocken.bots import Faustregel  # noqa: E402
from schocken.engine import spiele_spiel  # noqa: E402
from schocken.optimal import Optimal2, lade_loesung2  # noqa: E402


def lauf(args):
    gegner, seed, n = args
    rng = random.Random(seed)
    s = lade_loesung2()
    opt = Optimal2(s)
    andere = Optimal2(s) if gegner == "optimal" else Faustregel()
    verluste_starter = verluste_opt = 0
    for i in range(n):
        starter = i % 2
        e = spiele_spiel([opt, andere], rng, starter=starter)
        verluste_starter += e.verlierer == starter
        verluste_opt += e.verlierer == 0
    return verluste_starter, verluste_opt, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spiele", type=int, default=4000, help="je Prozess")
    args = ap.parse_args()
    s = lade_loesung2()
    erwartet = s.p_verlust(0)
    for gegner in ("optimal", "faustregel"):
        t = time.time()
        with Pool(4) as pool:
            r = np.array(pool.map(lauf, [(gegner, 100 + k, args.spiele) for k in range(4)])).sum(0)
        n = r[2]
        q_start, q_opt = r[0] / n, r[1] / n
        se = np.sqrt(0.25 / n)
        print(f"\nOptimal gegen {gegner}: {n} Spiele in {time.time() - t:.0f}s")
        print(f"  Spielbeginner verliert: {q_start:.4f} +- {1.96 * se:.4f}", end="")
        if gegner == "optimal":
            print(f"   (berechnet: {erwartet:.4f}, Abweichung {(q_start - erwartet) / se:+.2f} SE)")
        else:
            print()
        print(f"  Optimal verliert:       {q_opt:.4f} +- {1.96 * se:.4f}")


if __name__ == "__main__":
    main()
