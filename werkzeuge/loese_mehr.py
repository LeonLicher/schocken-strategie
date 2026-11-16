"""Konter-Näherung für 3 bis 6 Spieler: Stammtischwerte berechnen und per Simulation prüfen.

python werkzeuge/loese_mehr.py --spieler 3 --spiele 2000
Schonend: niedrige Priorität, Simulation mit 2 Prozessen.
"""

import argparse
import os
import pickle
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

os.environ.setdefault("NUMBA_NUM_THREADS", "1")
PROZESSE = int(os.environ.get("SCHOCKEN_PROZESSE", "2"))  # lokal schonend 2, in der Cloud mehr


def _niedrig():
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)


_niedrig()
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from schocken.bots import Stammtisch  # noqa: E402
from schocken.engine import spiele_spiel  # noqa: E402
from schocken.konter import lade_konter  # noqa: E402
from schocken.mehr import KonterNaeherung, Stammtischwerte, datei, lade_werte  # noqa: E402


def lauf(args):
    n, seed, spiele = args
    _niedrig()
    rng = random.Random(seed)
    werte = {n: lade_werte(n)}
    k2 = lade_konter(2)
    verloren = 0
    for i in range(spiele):
        bot = KonterNaeherung(werte, k2)
        e = spiele_spiel([bot] + [Stammtisch() for _ in range(n - 1)], rng, starter=i % n)
        verloren += e.verlierer == 0
    return verloren


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spieler", type=int, required=True)
    ap.add_argument("--spiele", type=int, default=2000, help="je Prozess (0 = nur berechnen)")
    a = ap.parse_args()
    n = a.spieler
    t = time.time()
    if not datei(n).exists():
        L = Stammtischwerte(n, lade_konter(2)).loese(melde=lambda s: print(f"[{time.time() - t:5.0f}s] {s}", flush=True))
        with open(datei(n), "wb") as f:
            pickle.dump(L, f)
    L = lade_werte(n)
    v0 = np.mean([L.wert("H1", 13, (0,) * n, s) for s in range(n)])
    print(f"Stammtischwerte für {n} Spieler fertig ({time.time() - t:.0f}s). "
          f"Alle Stammtisch (Konter nur im Finale): ich verliere {v0:.4f}", flush=True)
    if a.spiele:
        t = time.time()
        with Pool(PROZESSE, initializer=_niedrig) as pool:
            verloren = sum(pool.map(lauf, [(n, 50 + k, a.spiele) for k in range(PROZESSE)]))
        m = PROZESSE * a.spiele
        q = verloren / m
        print(f"Konter-Näherung gegen {n - 1}x Stammtisch: verliert {q:.4f} +- {1.96 * np.sqrt(q * (1 - q) / m):.4f} "
              f"({m} Spiele, {time.time() - t:.0f}s); fair wäre {1 / n:.4f}")


if __name__ == "__main__":
    main()
