"""Löst das echte Optimum zu dritt (alle spielen perfekt). Dauert einige Stunden.

Schonend: 2 Rechenkerne, niedrige Priorität. Speichert nach jeder Phase einen Zwischenstand und setzt
bei einem Neustart dort fort.

python werkzeuge/loese_optimum3.py
"""

import os
import pickle
import sys
import time
from pathlib import Path

os.environ.setdefault("NUMBA_NUM_THREADS", "2")
if sys.platform == "win32":
    import ctypes
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from schocken.gleichgewicht import ERGEBNISSE, GESAMT, Gleichgewicht3, speichere  # noqa: E402
from schocken.optimal import lade_loesung2  # noqa: E402

ZWISCHEN = ERGEBNISSE / "optimum3_zwischenstand.pkl"


def main():
    t = time.time()
    melde = lambda s: print(f"[{time.time() - t:7.0f}s] {s}", flush=True)  # noqa: E731
    G = Gleichgewicht3(lade_loesung2())
    if ZWISCHEN.exists():
        with open(ZWISCHEN, "rb") as f:
            G.V = pickle.load(f)
        melde(f"Zwischenstand geladen: {list(G.V)}")
    for phase in G.phasen():
        if phase in G.V and len(G.V[phase]) > 0 and (GESAMT, (0, 0, 0), 0) in G.V[phase]:
            melde(f"{phase} schon fertig")
            continue
        G.loese_phase(phase, toleranz=1e-7, melde=melde)
        with open(ZWISCHEN, "wb") as f:
            pickle.dump(G.V, f)
    speichere(G)
    ZWISCHEN.unlink(missing_ok=True)
    werte = [G.wert("H1", GESAMT, (0, 0, 0), s) for s in range(3)]
    melde("Fertig.")
    for s, v in enumerate(werte):
        print(f"  Spielbeginner Sitz {s}: P(verliert) Sitz 0/1/2 = {v[0]:.4f} / {v[1]:.4f} / {v[2]:.4f}")


if __name__ == "__main__":
    main()
