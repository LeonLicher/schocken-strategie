"""Prüft Konter per Simulation in der Referenz-Engine und vergleicht mit dem berechneten Wert.

python werkzeuge/pruefe_konter.py --spieler 2 --spiele 4000
Nutzt 2 Prozesse mit niedriger Priorität.
"""

import argparse
import os
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

os.environ.setdefault("NUMBA_NUM_THREADS", "1")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from schocken.bots import Stammtisch  # noqa: E402
from schocken.engine import spiele_spiel  # noqa: E402
from schocken.konter import Konter, lade_konter  # noqa: E402


def _niedrig():
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)


def lauf(args):
    n, seed, spiele, gegner = args
    rng = random.Random(seed)
    loesungen = {k: lade_konter(k) for k in (2, n)}
    verluste = np.zeros(n)
    for i in range(spiele):
        spieler = [Konter(loesungen)] + [Stammtisch() for _ in range(n - 1)] if gegner == "konter" else \
            [Stammtisch() for _ in range(n)]
        e = spiele_spiel(spieler, rng, starter=i % n)
        verluste[e.verlierer] += 1
    return verluste


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spieler", type=int, default=2)
    ap.add_argument("--spiele", type=int, default=4000, help="je Prozess")
    a = ap.parse_args()
    erwartet = lade_konter(a.spieler).p_verlust()
    for gegner in ("konter", "stammtisch"):
        t = time.time()
        with Pool(2, initializer=_niedrig) as pool:
            v = np.array(pool.map(lauf, [(a.spieler, 10 + k, a.spiele, gegner) for k in range(2)])).sum(0)
        n = v.sum()
        q = v[0] / n
        se = np.sqrt(q * (1 - q) / n)
        wer = "Konter" if gegner == "konter" else "Stammtisch (Sitz 0)"
        zusatz = f"   berechnet {erwartet:.4f}, Abweichung {(q - erwartet) / se:+.2f} SE" if gegner == "konter" else ""
        print(f"{wer} gegen {a.spieler - 1}x Stammtisch: verliert {q:.4f} +- {1.96 * se:.4f} "
              f"({int(n)} Spiele, {time.time() - t:.0f}s){zusatz}")


if __name__ == "__main__":
    main()
