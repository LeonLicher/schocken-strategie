"""Löst Konter (beste Antwort auf Stammtisch-Gegner) für 2 und 3 Spieler.

Schonend: höchstens 2 Rechenkerne, niedrige Priorität (der PC bleibt nutzbar), wenig Speicher.

python werkzeuge/loese_konter.py --spieler 2
python werkzeuge/loese_konter.py --spieler 3
"""

import argparse
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("NUMBA_NUM_THREADS", "2")
if sys.platform == "win32":
    import ctypes
    BELOW_NORMAL_PRIORITY_CLASS = 0x4000
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), BELOW_NORMAL_PRIORITY_CLASS)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from schocken.konter import KonterLoesung, lade_konter, speichere  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spieler", type=int, choices=(2, 3), required=True)
    a = ap.parse_args()
    t = time.time()
    zwei = lade_konter(2) if a.spieler == 3 else None
    L = KonterLoesung(a.spieler, zwei)
    L.loese(melde=lambda s: print(f"[{time.time() - t:6.0f}s] {s}", flush=True))
    speichere(L)
    print(f"\nFertig in {time.time() - t:.0f}s. P(Konter verliert gegen {a.spieler - 1} Stammtisch-Spieler, "
          f"zufälliger Spielbeginner) = {L.p_verlust():.4f}  (fair wäre {1 / a.spieler:.4f})")


if __name__ == "__main__":
    main()
