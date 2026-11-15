"""Wo spielt Konter anders als der Stammtisch? (Spielbeginn, Hälfte 1, alle 0 Deckel)

python werkzeuge/analyse_konter.py --spieler 3
"""

import argparse
import os
import sys
from itertools import combinations_with_replacement
from pathlib import Path

import numpy as np

os.environ.setdefault("NUMBA_NUM_THREADS", "1")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from schocken.bots import stammtisch_entscheidung  # noqa: E402
from schocken.konter import F_FOLGER, S_START, _starter_bewertung, folger_bewertung_allgemein, lade_konter  # noqa: E402
from schocken.loeser import ACT_H, ACT_N, ACT_T, D_ID, GESAMT, H_ID, W, W_VON, WERTUNGEN, _W_ID, wahl, zug_dp  # noqa: E402
from schocken.wertung import bewerte  # noqa: E402


def text(wuerfel, j, d, m, s, verdeckt):
    if j < 0:
        return "stehen lassen"
    from schocken.loeser import behalten_von
    h, t = ACT_H[d, m, s, j], ACT_T[d, m, s, j]
    halten = sorted(list(behalten_von(h, t)) + [1] * int(t), reverse=True)
    return ("halte " + "-".join(map(str, halten)) if halten else "alle neu") + (" (gedreht)" if t else "") + \
        (", verdeckt" if verdeckt else "")


def stammtisch_text(k, wuerfel, neu, grenze, starter):
    e = stammtisch_entscheidung(k, wuerfel, neu, grenze, starter)
    if e is None:
        return "stehen lassen"
    halten = sorted(list(e[0]) + [1] * e[1], reverse=True)
    return ("halte " + "-".join(map(str, halten)) if halten else "alle neu") + (" (gedreht)" if e[1] else "")


def wert_von(Uo, Uv, EV, k, d, m, s, j, verdeckt):
    if j < 0:
        return Uo[W_VON[d, 1 if m == 3 else 0], k]
    h = ACT_H[d, m, s, j]
    return Uv[h, k + 1] if verdeckt else EV[k + 1, h]


def aktion_index(d, m, s, behalten, drehen):
    h = H_ID[tuple(sorted(tuple(behalten) + (1,) * drehen))]
    for j in range(ACT_N[d, m, s]):
        if ACT_H[d, m, s, j] == h:
            return j
    return None


def vergleiche_zug(titel, Uo, Uv, grenze, darf, vm, starter, wuerfe_liste):
    _, V, EV = zug_dp(Uo, Uv, grenze, darf, vm)
    print(f"\n{titel}")
    anders = 0
    for k, wuerfel, neu in wuerfe_liste:
        d, m, s = D_ID[tuple(sorted(wuerfel))], len(neu), list(neu).count(6)
        j, verdeckt = wahl(V, EV, Uo, Uv, grenze, darf, vm, k, d, m, s)
        e = stammtisch_entscheidung(k, wuerfel, neu, grenze, starter)
        jb = -1 if e is None else aktion_index(d, m, s, e[0], e[1])
        q_opt = wert_von(Uo, Uv, EV, k, d, m, s, j, verdeckt)
        q_st = wert_von(Uo, Uv, EV, k, d, m, s, jb, vm and k + 1 == grenze)
        gewinn = (q_opt - q_st) * 100
        if gewinn > 0.05:
            anders += 1
            print(f"  Wurf {k}: {'-'.join(map(str, sorted(wuerfel, reverse=True)))} ({m} neu): Stammtisch "
                  f"{stammtisch_text(k, wuerfel, neu, grenze, starter):18s} → Konter {text(wuerfel, j, d, m, s, verdeckt):24s} "
                  f"(+{gewinn:.1f} %-Pkt.)")
    if not anders:
        print("  keine nennenswerten Unterschiede")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spieler", type=int, default=3)
    a = ap.parse_args()
    n = a.spieler
    L = lade_konter(n)
    print(f"P(Konter verliert gegen {n - 1}x Stammtisch) = {L.p_verlust():.4f}, fair {1 / n:.4f}")
    deckel = (0,) * n
    Vn = L.vnext("H1", GESAMT, deckel)
    seats = np.array(list(range(n)) + [0] * (3 - n), dtype=np.int64)

    wuerfe1 = [(1, w, w) for w in combinations_with_replacement(range(1, 7), 3)]
    wuerfe2 = [(2, (1,) + w, w) for w in combinations_with_replacement(range(1, 7), 2)] + \
              [(2, w, w) for w in combinations_with_replacement(range(1, 7), 3)]
    Uo, Uv = _starter_bewertung(n, seats, F_FOLGER, Vn)
    vergleiche_zug("ICH BEGINNE (Spielbeginn): wo Konter anders spielt als der Stammtisch", Uo, Uv, 3, True, False,
                   True, wuerfe1 + wuerfe2)

    # Ich bin Zweiter; der Stammtisch-Startspieler hat ein typisches Ergebnis
    for erg, k1 in [((6, 5, 3), 1), ((4, 2, 1), 2), ((5, 1, 1), 2), ((6, 4, 2), 3)]:
        w1 = _W_ID[bewerte(erg, False)]
        D_vor = np.zeros((3, W, 4))
        D_vor[0, w1, k1] = 1.0
        seats2 = np.array([1, 0, 2][:n] + [0] * (3 - n), dtype=np.int64)
        Vn2 = L.vnext("H1", GESAMT, deckel)
        Uo, Uv = folger_bewertung_allgemein(n, seats2, 1, D_vor, k1, F_FOLGER, Vn2, False)
        liste = [w for w in wuerfe1 + wuerfe2 if w[0] < k1]
        vergleiche_zug(f"ICH BIN ZWEITER, Startspieler hat {WERTUNGEN[w1].name} nach {k1} Wurf/Würfen", Uo, Uv, k1,
                       False, False, False, liste)


if __name__ == "__main__":
    main()
