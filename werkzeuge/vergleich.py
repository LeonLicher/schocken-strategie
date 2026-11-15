"""Prüft den schnellen Simulator statistisch gegen die Referenz-Engine.

python werkzeuge/vergleich.py
"""

import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from schocken.bots import ParameterStrategie  # noqa: E402
from schocken.engine import spiele_spiel  # noqa: E402
from schocken.schnell import verlustquoten  # noqa: E402

# Drei bewusst unterschiedliche Strategien, damit die Verlustquoten deutlich verschieden sind.
P = [(1, 0, 1, 0, 1), (5, 3, 2, 0, 0), (3, 2, 0, 200, 1)]


def referenz(seed, n=3000):
    rng = random.Random(seed)
    v = [0] * len(P)
    for _ in range(n):
        v[spiele_spiel([ParameterStrategie(p) for p in P], rng).verlierer] += 1
    return v


def main():
    t = time.time()
    with Pool(4) as pool:
        res = np.array(pool.map(referenz, range(8))).sum(0)
    n_ref = res.sum()
    q_ref = res / n_ref
    print(f"Referenz: {n_ref} Spiele in {time.time() - t:.0f}s -> {np.round(q_ref, 4)}")

    verlustquoten(P, 1000, 1)  # kompilieren
    t = time.time()
    n = 4_000_000
    q, f = verlustquoten(P, n, 7)
    dt = time.time() - t
    print(f"Schnell: {n} Spiele in {dt:.1f}s = {n / dt:,.0f} Spiele/s -> {np.round(q, 4)} +- {np.round(f, 4)}")
    se = np.sqrt(q_ref * (1 - q_ref) / n_ref)
    print("Abweichung in Standardfehlern:", np.round((q_ref - q) / se, 2))


if __name__ == "__main__":
    main()
