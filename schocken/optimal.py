"""Optimaler Spieler für Schocken zu zweit (nutzt die exakte Lösung aus loeser.py)."""

import pickle
from pathlib import Path

import numpy as np

from .engine import STOPP, Aktion, Sicht, Strategie
from .loeser import (ACT_H, ACT_T, D_ID, H_ID, P_VERDECKT, W, _W_ID, behalten_von, folger_bewertung,
                     loese_spiel2, starter_bewertung, wahl, zug_dp)

LOESUNG2 = Path(__file__).resolve().parent.parent / "ergebnisse" / "loesung2.pkl"


def lade_loesung2():
    if LOESUNG2.exists():
        with open(LOESUNG2, "rb") as f:
            return pickle.load(f)
    s = loese_spiel2()
    LOESUNG2.parent.mkdir(exist_ok=True)
    with open(LOESUNG2, "wb") as f:
        pickle.dump(s, f)
    return s


class Optimal2(Strategie):
    """Spielt jede Entscheidung optimal, um das Spiel (zu zweit) möglichst selten zu verlieren."""

    name = "Optimal"

    def __init__(self, loesung=None):
        self.s = loesung or lade_loesung2()
        self._cache = {}

    def _kontext(self, sicht: Sicht):
        if len(sicht.deckel) != 2:
            raise ValueError("Optimal2 ist nur für 2 Spieler gelöst.")
        h = self.s.haelfte(sicht.haelfte, sicht.haelften_verlierer)
        d = dict(sicht.deckel)
        starter = sicht.spieler if sicht.ist_starter else sicht.bisher[0].spieler
        return h, sicht.mitte, d[0], starter

    def _tabellen(self, sicht: Sicht):
        h, mitte, d0, starter = self._kontext(sicht)
        if sicht.ist_starter:
            schluessel = (id(h), mitte, d0, starter)
        else:
            e = sicht.bisher[0]
            ende = ("v", H_ID[tuple(sorted(e.sichtbar))]) if e.verdeckt else ("o", _W_ID[e.wertung])
            schluessel = (id(h), mitte, d0, starter, ende, e.wuerfe)
        if schluessel in self._cache:
            return self._cache[schluessel]
        A, B = h.AB(mitte, d0, starter)
        if sicht.ist_starter:
            Uo, Uv = starter_bewertung(A, B)
            args = (Uo, Uv, 3, True, False)
        else:
            if e.verdeckt:
                p1, vm = P_VERDECKT[H_ID[tuple(sorted(e.sichtbar))]], True
            else:
                p1, vm = np.zeros(W), False
                p1[_W_ID[e.wertung]] = 1.0
            Uo, Uv = folger_bewertung(p1, e.wuerfe, A, B, vm)
            args = (Uo, Uv, e.wuerfe, False, vm)
        wert, V, EV = zug_dp(*args)
        self._cache[schluessel] = (V, EV, args, wert)
        return self._cache[schluessel]

    def wert(self, sicht: Sicht) -> float:
        """Erwartungswert des eigenen Zugs aus Sicht der Lösung (für Auswertungen)."""
        return self._tabellen(sicht)[3]

    def entscheide(self, sicht: Sicht) -> Aktion:
        V, EV, (Uo, Uv, grenze, darf, vm), _ = self._tabellen(sicht)
        if sicht.phase == "vor_wurf":
            return Aktion(verdeckt=bool(Uv[0, 1] > EV[1, 0] + 1e-12))
        d = D_ID[tuple(sorted(sicht.wuerfel))]
        m, s = len(sicht.neu), sicht.neu.count(6)
        j, verdeckt = wahl(V, EV, Uo, Uv, grenze, darf, vm, sicht.wurf_nr, d, m, s)
        if j < 0:
            return STOPP
        h, t = ACT_H[d, m, s, j], ACT_T[d, m, s, j]
        return Aktion(behalten=behalten_von(h, t), drehen=int(t), verdeckt=bool(verdeckt))
