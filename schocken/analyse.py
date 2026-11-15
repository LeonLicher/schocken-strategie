"""Abfragen und Auswerten der exakten 2-Spieler-Lösung aus Sicht eines Spielers ("ich" = Spieler 0).

- `Lage`: Spielstand aus meiner Sicht.
- `optionen`: alle Möglichkeiten in einer Situation mit meiner Verlustwahrscheinlichkeit.
- `vergleiche_zug`: findet alle Zustände eines Zugs, in denen die beste Entscheidung von einer Basis abweicht.
"""

from dataclasses import dataclass

import numpy as np
from numba import njit

from .loeser import (ACT_H, ACT_N, ACT_T, D_ID, D_LISTE, GESAMT, H_GROESSE, H_ID, H_LISTE, NH, P_VERDECKT,
                     ROLL_D, ROLL_N, ROLL_P, ROLL_S, W, W_VON, WERTUNGEN, _W_ID, folger_bewertung,
                     starter_bewertung, wahl, zug_dp)
from .wertung import bewerte


@dataclass(frozen=True)
class Lage:
    haelfte: str  # "Hälfte 1", "Hälfte 2" oder "Finale"
    h1_verlierer: str | None  # bei Hälfte 2: "ich" oder "gegner"
    mitte: int
    ich: int
    gegner: int
    start: str  # wer die Runde beginnt: "ich" oder "gegner"

    def __post_init__(self):
        assert self.mitte + self.ich + self.gegner == GESAMT, self

    def text(self) -> str:
        h = self.haelfte
        if h == "Hälfte 2":
            h += " (H1 verloren: " + ("ich" if self.h1_verlierer == "ich" else "Gegner") + ")"
        return f"{h}, Mitte {self.mitte}, ich {self.ich} : Gegner {self.gegner}, Start: {self.start}"


NEUTRAL_STARTER = Lage("Hälfte 1", None, GESAMT, 0, 0, "ich")
NEUTRAL_FOLGER = Lage("Hälfte 1", None, GESAMT, 0, 0, "gegner")


@dataclass
class Tabellen:
    """Ergebnis eines Zug-Löses. Werte q: Starter = -P(ich verliere), Folger = P(Gegner verliert)."""

    Uo: np.ndarray
    Uv: np.ndarray
    V: np.ndarray
    EV: np.ndarray
    grenze: int
    darf: bool
    vm: bool
    ich_starter: bool

    def p_verlust(self, q: float) -> float:
        return -q if self.ich_starter else 1.0 - q

    @property
    def args(self):
        return self.Uo, self.Uv, self.grenze, self.darf, self.vm


def _AB(s, lage: Lage):
    l1 = 0 if lage.h1_verlierer == "ich" else 1
    h = s.haelfte(lage.haelfte, (l1,))
    starter = 0 if lage.start == "ich" else 1
    return h.AB(lage.mitte, lage.ich, starter)


def starter_tabellen(s, lage: Lage, cache=None) -> Tabellen:
    """Tabellen für den Startspieler der Lage (ich, wenn lage.start == "ich", sonst der Gegner)."""
    if cache is not None and lage in cache:
        return cache[lage]
    A, B = _AB(s, lage)
    Uo, Uv = starter_bewertung(A, B)
    _, V, EV = zug_dp(Uo, Uv, 3, True, False)
    t = Tabellen(Uo, Uv, V, EV, 3, True, False, lage.start == "ich")
    if cache is not None:
        cache[lage] = t
    return t


def folger_tabellen(s, lage: Lage, ende) -> Tabellen:
    """Tabellen für mich als Folgespieler. ende = ("o", w1, k1) oder ("v", h1, k1) des Gegners."""
    A, B = _AB(s, lage)
    art, x, k1 = ende
    if art == "v":
        p1, vm = P_VERDECKT[x], True
    else:
        p1, vm = np.zeros(W), False
        p1[x] = 1.0
    Uo, Uv = folger_bewertung(p1, k1, A, B, vm)
    _, V, EV = zug_dp(Uo, Uv, k1, False, vm)
    return Tabellen(Uo, Uv, V, EV, k1, False, vm, False)


def ende_text(ende) -> str:
    art, x, k = ende
    if art == "v":
        sichtbar = "".join(map(str, sorted(H_LISTE[x], reverse=True))) or "nichts"
        return f"Gegner verdeckt nach {k} (sichtbar: {sichtbar})"
    return f"Gegner {WERTUNGEN[x].name} nach {k}"


def aktion_text(d, m, s, j, verdeckt) -> str:
    if j == -2:
        return "verdeckt beginnen" if verdeckt else "offen beginnen"
    if j < 0:
        return "fertig"
    h, t = ACT_H[d, m, s, j], ACT_T[d, m, s, j]
    teile = ["halte " + ("".join(map(str, sorted(H_LISTE[h], reverse=True))) or "nichts")]
    if t:
        teile.append(f"({t + 1}x6 -> {t}x1)")
    if verdeckt:
        teile.append("VERDECKT")
    return " ".join(teile)


def zustand(wuerfel, neu):
    """(d, m, s) aus Würfeln und den davon neu geworfenen Würfeln."""
    return D_ID[tuple(sorted(wuerfel))], len(neu), list(neu).count(6)


def optionen(t: Tabellen, k, d, m, s):
    """Alle Möglichkeiten nach Wurf k im Zustand (d, m, s): Liste (text, P(ich verliere)), beste zuerst."""
    Uo, Uv, V, EV = t.Uo, t.Uv, t.V, t.EV
    res = [("fertig", t.p_verlust(Uo[W_VON[d, 1 if m == 3 else 0], k]))]
    rest = t.grenze - k
    if rest > 0:
        for j in range(ACT_N[d, m, s]):
            if ACT_T[d, m, s, j] > rest:
                continue
            h = ACT_H[d, m, s, j]
            erzwungen = t.vm and k + 1 == t.grenze
            if not erzwungen:
                res.append((aktion_text(d, m, s, j, False), t.p_verlust(EV[k + 1, h])))
            if t.darf or erzwungen:
                res.append((aktion_text(d, m, s, j, True), t.p_verlust(Uv[h, k + 1])))
    return sorted(res, key=lambda x: x[1])


# --------------------------------------------------------------------------- Abweichungen


@njit(cache=True)
def _q(V, EV, Uo, Uv, grenze, darf, vm, k, d, m, s, j, verdeckt):
    if j < 0:
        return Uo[W_VON[d, 1 if m == 3 else 0], k]
    h = ACT_H[d, m, s, j]
    if verdeckt:
        return Uv[h, k + 1]
    return EV[k + 1, h]


@njit(cache=True)
def vergleiche_zug(V, EV, Uo, Uv, Vb, EVb, Uob, Uvb, grenze, darf, vm):
    """Geht alle unter optimalem Spiel erreichbaren Zustände eines Zugs durch.

    Rückgabe:
      rec: Zeilen (k, d, m, s, P(Zustand), Gewinn, j_opt, verdeckt_opt, j_basis, verdeckt_basis)
           für Zustände, in denen die Basis (Tabellen *b) eine schlechtere Entscheidung trifft.
           Gewinn in Einheiten von q (= Verlustwahrscheinlichkeit). k = 0: Entscheidung vor dem 1. Wurf.
      T_offen[w, k], T_verdeckt[h, k]: Verteilung der Zug-Enden unter optimalem Spiel.
      erreicht[k, d, m, s]: Wahrscheinlichkeit, den Entscheidungszustand zu erreichen.
    """
    rec = np.zeros((4 * 56 * 4 * 4 + 1, 10))
    n = 0
    T_offen = np.zeros((W, 4))
    T_verdeckt = np.zeros((NH, 4))
    erreicht = np.zeros((4, 56, 4, 4))
    if darf:
        opt_v = Uv[0, 1] > EV[1, 0] + 1e-12
        basis_v = Uvb[0, 1] > EVb[1, 0] + 1e-12
        if opt_v != basis_v:
            q_opt = Uv[0, 1] if opt_v else EV[1, 0]
            q_basis = Uv[0, 1] if basis_v else EV[1, 0]
            if q_opt - q_basis > 1e-12:
                rec[n, 0], rec[n, 4], rec[n, 5] = 0, 1.0, q_opt - q_basis
                rec[n, 6], rec[n, 7], rec[n, 8], rec[n, 9] = -2, opt_v, -2, basis_v
                n += 1
        if opt_v:
            T_verdeckt[0, 1] = 1.0
            return rec[:n], T_offen, T_verdeckt, erreicht
    elif vm and grenze == 1:
        T_verdeckt[0, 1] = 1.0
        return rec[:n], T_offen, T_verdeckt, erreicht

    front = np.zeros(NH)
    front[0] = 1.0
    for k in range(1, grenze + 1):
        reach = np.zeros((56, 4, 4))
        for h in range(NH):
            if front[h] == 0.0:
                continue
            m = 3 - H_GROESSE[h]
            for j in range(ROLL_N[h]):
                reach[ROLL_D[h, j], m, ROLL_S[h, j]] += front[h] * ROLL_P[h, j]
        erreicht[k] = reach
        front = np.zeros(NH)
        for d in range(56):
            for m in range(1, 4):
                for s in range(4):
                    p = reach[d, m, s]
                    if p == 0.0:
                        continue
                    adh = 1 if m == 3 else 0
                    if k == grenze:
                        T_offen[W_VON[d, adh], k] += p
                        continue
                    jo, vo = wahl(V, EV, Uo, Uv, grenze, darf, vm, k, d, m, s)
                    jb, vb = wahl(Vb, EVb, Uob, Uvb, grenze, darf, vm, k, d, m, s)
                    if jo != jb or (jo >= 0 and vo != vb):
                        gewinn = (_q(V, EV, Uo, Uv, grenze, darf, vm, k, d, m, s, jo, vo)
                                  - _q(V, EV, Uo, Uv, grenze, darf, vm, k, d, m, s, jb, vb))
                        if gewinn > 1e-12:
                            rec[n, 0], rec[n, 1], rec[n, 2], rec[n, 3] = k, d, m, s
                            rec[n, 4], rec[n, 5] = p, gewinn
                            rec[n, 6], rec[n, 7], rec[n, 8], rec[n, 9] = jo, vo, jb, vb
                            n += 1
                    if jo < 0:
                        T_offen[W_VON[d, adh], k] += p
                    elif vo:
                        T_verdeckt[ACT_H[d, m, s, jo], k + 1] += p
                    else:
                        front[ACT_H[d, m, s, jo]] += p
    return rec[:n], T_offen, T_verdeckt, erreicht


def wuerfel_text(d) -> str:
    return "-".join(map(str, sorted(D_LISTE[d], reverse=True)))


__all__ = ["Lage", "NEUTRAL_STARTER", "NEUTRAL_FOLGER", "Tabellen", "starter_tabellen", "folger_tabellen",
           "optionen", "vergleiche_zug", "aktion_text", "ende_text", "zustand", "wuerfel_text",
           "H_ID", "_W_ID", "bewerte"]
