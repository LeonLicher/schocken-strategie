"""Exportiert das echte Optimum zu dritt für die Website (dauert rund 40 Minuten, 2 Kerne, niedrige Priorität).

- site/daten/optimum3.json: Werte aller Spielstände (P(Sitz i verliert)), P(Startspieler verliert das Finale),
  und je Spielstand mit drei aktiven Spielern den Index seiner Startspieler-Tabelle.
- site/daten/optimum3_start.bin: Float32, je Spielstand N_T1 Werte: P(Startspieler verliert), wenn er mit
  Zug-Ende t aufhört (Reihenfolge wie gleichgewicht._T1). Damit entscheidet der Startspieler im Browser sofort;
  die anderen Spieler rechnet der Browser live.

Prüft nebenbei, dass die Tabellen den gespeicherten Wert jedes Spielstands reproduzieren.

python werkzeuge/export_optimum3.py
"""

import json
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

import numpy as np  # noqa: E402

from schocken.gleichgewicht import ERGEBNISSE, GESAMT, N_T1, T1_ART, T1_K, T1_X, _spiele_zug, lade_optimum3, \
    starter_q, NH, W  # noqa: E402

SITE = Path(__file__).resolve().parent.parent / "site" / "daten"
ZWISCHEN = ERGEBNISSE / "optimum3_start_zwischenstand.pkl"


def phasen_name(phase):
    return phase if phase == "H1" else f"H2_{phase[1]}"


def main():
    t0 = time.time()
    melde = lambda s: print(f"[{time.time() - t0:7.0f}s] {s}", flush=True)  # noqa: E731
    G = lade_optimum3()
    fertig = {}
    if ZWISCHEN.exists():
        with open(ZWISCHEN, "rb") as f:
            fertig = pickle.load(f)
        melde(f"Zwischenstand: {len(fertig)} Spielstände")
    zeilen, bloecke, max_abw = {}, [], 0.0
    for phase in G.phasen():
        name = phasen_name(phase)
        zeilen[name] = []
        for z, v in sorted(G.V[phase].items(), key=lambda x: (x[0][0], x[0][1], x[0][2])):
            mitte, deckel, starter = z
            reihe = G.reihenfolge(mitte, deckel, starter)
            idx = -1
            if len(reihe) == 3:
                schl = (name, z)
                if schl not in fertig:
                    seats = np.array(reihe, dtype=np.int64)
                    Q = starter_q(seats, G.vnext(phase, mitte, deckel))
                    E_o, E_v = np.zeros((W, 4, 3)), np.zeros((NH, 4, 3))
                    for t in range(N_T1):
                        (E_o if T1_ART[t] == 0 else E_v)[T1_X[t], T1_K[t]] = Q[t]
                    abw = float(np.abs(_spiele_zug(E_o, E_v, seats[0], 3, True, False) - v).max())
                    fertig[schl] = (Q[:, reihe[0]].astype(np.float32), abw)
                    if len(fertig) % 200 == 0:
                        with open(ZWISCHEN, "wb") as f:
                            pickle.dump(fertig, f)
                        melde(f"{len(fertig)} Spielstände, zuletzt {name} {z}")
                q, abw = fertig[schl]
                max_abw = max(max_abw, abw)
                idx = len(bloecke)
                bloecke.append(q)
            zeilen[name].append([mitte, *deckel, starter, *[round(float(x), 10) for x in v], idx])
    melde(f"Größte Abweichung Tabelle gegen gespeicherten Wert: {max_abw:.2e}")
    f0 = float(G.zwei.finale.wert(GESAMT, 0, 0))
    SITE.mkdir(parents=True, exist_ok=True)
    with open(SITE / "optimum3.json", "w", encoding="utf-8") as f:
        json.dump({"n_t1": N_T1, "t1": [[int(a), int(x), int(k)] for a, x, k in zip(T1_ART, T1_X, T1_K)],
                   "f0": f0, "V": zeilen}, f, separators=(",", ":"))
    np.concatenate(bloecke).astype("<f4").tofile(SITE / "optimum3_start.bin")
    melde(f"geschrieben: {sum(len(z) for z in zeilen.values())} Spielstände, {len(bloecke)} Startspieler-Tabellen")
    ZWISCHEN.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
