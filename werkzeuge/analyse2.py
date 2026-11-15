"""Was macht die optimale 2-Spieler-Strategie? Auswertung der exakten Lösung.

python werkzeuge/analyse2.py
"""

import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from schocken.loeser import (ACT_H, ACT_T, D_LISTE, GESAMT, H_LISTE, P_VERDECKT, ROLL_D, ROLL_N, ROLL_P,  # noqa: E402
                             ROLL_S, W, WERTUNGEN, W_VON, folger_bewertung, starter_bewertung, wahl, zug_dp)
from schocken.optimal import lade_loesung2  # noqa: E402


def text(d, m, s, j, verdeckt):
    if j < 0:
        return "fertig"
    h, t = ACT_H[d, m, s, j], ACT_T[d, m, s, j]
    teile = ["halte " + ("".join(map(str, H_LISTE[h])) or "nichts")]
    if t:
        teile.append(f"({t}x gedreht)")
    if verdeckt:
        teile.append("VERDECKT")
    return " ".join(teile)


def starter_politik(h, mitte, d0, starter):
    A, B = h.AB(mitte, d0, starter)
    Uo, Uv = starter_bewertung(A, B)
    wert, V, EV = zug_dp(Uo, Uv, 3, True, False)
    return Uo, Uv, V, EV, -wert


def zustandsverteilung(Uo, Uv, V, EV, grenze, darf, vm):
    """Wahrscheinlichkeit jedes Entscheidungszustands und der Zug-Enden unter optimalem Spiel."""
    p_zust = Counter()
    enden = Counter()
    if darf and Uv[0, 1] > EV[1, 0] + 1e-12:
        enden[("verdeckt", 0, 1)] += 1.0
        return p_zust, enden
    front = {0: 1.0}  # gehalten h -> Wahrscheinlichkeit, offen werfen
    for k in range(1, grenze + 1):
        neu_front = Counter()
        for h, ph in front.items():
            m = 3 - len(H_LISTE[h])
            for j in range(ROLL_N[h]):
                d, s, p = ROLL_D[h, j], ROLL_S[h, j], ph * ROLL_P[h, j]
                p_zust[(k, d, m, s)] += p
                if k == grenze:
                    enden[("offen", W_VON[d, 1 if m == 3 else 0], k)] += p
                    continue
                jj, verdeckt = wahl(V, EV, Uo, Uv, grenze, darf, vm, k, d, m, s)
                if jj < 0:
                    enden[("offen", W_VON[d, 1 if m == 3 else 0], k)] += p
                elif verdeckt or (vm and k + 1 == grenze):
                    enden[("verdeckt", ACT_H[d, m, s, jj], k + 1)] += p
                else:
                    neu_front[ACT_H[d, m, s, jj]] += p
        front = neu_front
    return p_zust, enden


def main():
    s = lade_loesung2()
    f = s.finale
    print(f"Finale-Start: P(Startspieler verliert) = {f.wert(GESAMT, 0, 0):.4f}")
    Uo, Uv, V, EV, _ = starter_politik(f, GESAMT, 0, 0)
    print(f"Verdeckt beginnen? Wert verdeckt {Uv[0, 1]:.4f} vs offen {EV[1, 0]:.4f} (höher = besser für Starter)")

    print("\nStartspieler, Finale-Beginn, nach Wurf 1 (alle 3 Würfel geworfen):")
    for d, wurf in enumerate(D_LISTE):
        sechs = wurf.count(6)
        j, vd = wahl(V, EV, Uo, Uv, 3, True, False, 1, d, 3, sechs)
        print(f"  {''.join(map(str, sorted(wurf, reverse=True)))}: {text(d, 3, sechs, j, vd)}")

    p_zust, enden = zustandsverteilung(Uo, Uv, V, EV, 3, True, False)
    wuerfe = Counter()
    verdeckt = 0.0
    for (art, _, k), p in enden.items():
        wuerfe[k] += p
        if art == "verdeckt":
            verdeckt += p
    print("\nWie viele Würfe nutzt der Startspieler (Finale-Beginn)?")
    for k in (1, 2, 3):
        print(f"  {k}: {wuerfe[k]:.3f}")
    print(f"  davon letzter Wurf verdeckt: {verdeckt:.3f}")

    # Über alle Zustände: wie oft spielt der Startspieler verdeckt?
    print("\nAnteil verdeckter Züge des Startspielers je Spielstand (Finale):")
    for mitte, d0 in [(13, 0), (6, 3), (0, 6), (0, 1), (0, 12)]:
        Uo, Uv, V, EV, wert = starter_politik(f, mitte, d0, 0)
        _, enden = zustandsverteilung(Uo, Uv, V, EV, 3, True, False)
        anteil = sum(p for (art, _, _), p in enden.items() if art == "verdeckt")
        verteilung = Counter()
        for (_, _, k), p in enden.items():
            verteilung[k] += p
        print(f"  Mitte {mitte:2d}, eigene Deckel {d0:2d}: verdeckt {anteil:.3f}, "
              f"Würfe 1/2/3 = {verteilung[1]:.2f}/{verteilung[2]:.2f}/{verteilung[3]:.2f}, "
              f"P(verliert Spiel) {wert:.3f}")


if __name__ == "__main__":
    main()
