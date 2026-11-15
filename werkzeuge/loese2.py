"""Löst Schocken zu zweit exakt und speichert die Lösung.

python werkzeuge/loese2.py
"""

import pickle
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from schocken.loeser import GESAMT, loese_spiel2, runde2  # noqa: E402

ZIEL = Path(__file__).resolve().parent.parent / "ergebnisse" / "loesung2.pkl"


def main():
    t = time.time()
    runde2(np.ones(8) * 0.5, np.ones(8) * 0.5)
    print(f"Kompilieren: {time.time() - t:.1f}s")
    t = time.time()
    for _ in range(5):
        runde2(np.linspace(0, 1, 8), np.linspace(1, 0, 8))
    print(f"Eine Runde lösen: {(time.time() - t) / 5 * 1000:.0f} ms")

    t = time.time()
    s = loese_spiel2()
    print(f"Komplettes Spiel gelöst in {time.time() - t:.0f}s")
    ZIEL.parent.mkdir(exist_ok=True)
    with open(ZIEL, "wb") as f:
        pickle.dump(s, f)

    p0 = s.p_verlust(0)
    p1 = s.p_verlust(1)
    print(f"\nP(Spieler 0 verliert das Spiel), wenn er das Spiel beginnt: {p0:.5f}")
    print(f"P(Spieler 0 verliert das Spiel), wenn der andere beginnt:  {p1:.5f}")
    print(f"Finale: P(Startspieler verliert) = {s.finale.wert(GESAMT, 0, 0):.5f}")
    print("\nFinale, Mitte leer, P(Startspieler 0 verliert) je nach eigenen Deckeln:")
    for d0 in range(1, 13):
        print(f"  {d0:2d} Deckel (Gegner {13 - d0:2d}): {s.finale.wert(0, d0, 0):.4f}")


if __name__ == "__main__":
    main()
