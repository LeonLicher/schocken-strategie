"""Exakte Lösung per Rückwärtsrechnung.

Baustein 1, `zug_dp`: optimaler Zug eines Spielers bei gegebener Bewertung aller möglichen Zug-Enden.
    Zug-Ende offen:    (Wertung w, Wurfzahl k)    -> U_offen[w, k]
    Zug-Ende verdeckt: (gehaltene Würfel h, k)    -> U_verdeckt[h, k]   (Ergebnis = h + Zufallswurf)
    Zustand nach einem Wurf: (k, Würfel D, m = Anzahl neu geworfener Würfel, s = Sechsen unter den neuen)

Baustein 2, `runde2`: eine Runde zu zweit. Der Folgespieler antwortet optimal auf jedes mögliche
    Ergebnis des Startspielers; der Startspieler optimiert darüber.

Baustein 3, `loese_spiel2`: Wertiteration über alle Deckelstände für Hälfte 1, Hälfte 2 und Finale.
    Ergebnis: Wahrscheinlichkeit, das Spiel zu verlieren, für jeden Zustand bei beidseitig optimalem Spiel.
"""

from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations, combinations_with_replacement, product

import numpy as np
from numba import njit

from .wertung import SCHOCK_AUS, alle_wertungen, bewerte

# --------------------------------------------------------------------------- Tabellen

WERTUNGEN = alle_wertungen()  # aufsteigend nach Rang
W = len(WERTUNGEN)
_W_ID = {w: i for i, w in enumerate(WERTUNGEN)}
RANG_W = np.array([w.rang for w in WERTUNGEN], dtype=np.int64)
# Deckel-Index 1..6, Schock Aus = 7
DECK_W = np.array([7 if w.klasse == SCHOCK_AUS else w.deckel for w in WERTUNGEN], dtype=np.int64)
AUS = 7

D_LISTE = list(combinations_with_replacement(range(1, 7), 3))  # 56 Würfe (aufsteigend sortiert)
D_ID = {d: i for i, d in enumerate(D_LISTE)}
H_LISTE = [()] + [(a,) for a in range(1, 7)] + list(combinations_with_replacement(range(1, 7), 2))  # 28
H_ID = {h: i for i, h in enumerate(H_LISTE)}
NH = len(H_LISTE)
H_GROESSE = np.array([len(h) for h in H_LISTE], dtype=np.int64)
SECHSEN = np.array([d.count(6) for d in D_LISTE], dtype=np.int64)

W_VON = np.zeros((56, 2), dtype=np.int64)
for _d, _t in enumerate(D_LISTE):
    for _adh in range(2):
        W_VON[_d, _adh] = _W_ID[bewerte(_t, bool(_adh))]

# Würfeln mit gehaltenen Würfeln h: Verteilung über (Wurf D, Sechsen unter den neuen s)
ROLL_N = np.zeros(NH, dtype=np.int64)
ROLL_D = np.zeros((NH, 56), dtype=np.int64)
ROLL_S = np.zeros((NH, 56), dtype=np.int64)
ROLL_P = np.zeros((NH, 56))
P_VERDECKT = np.zeros((NH, W))  # Verteilung der Wertung, wenn mit h verdeckt gewürfelt wird
for _h, _ht in enumerate(H_LISTE):
    _r = 3 - len(_ht)
    _vert = defaultdict(float)
    for _wurf in product(range(1, 7), repeat=_r):
        _d = D_ID[tuple(sorted(_ht + _wurf))]
        _vert[(_d, _wurf.count(6))] += 6.0 ** -_r
        P_VERDECKT[_h, W_VON[_d, 1 if _r == 3 else 0]] += 6.0 ** -_r
    for _j, ((_d, _s), _p) in enumerate(sorted(_vert.items())):
        ROLL_D[_h, _j], ROLL_S[_h, _j], ROLL_P[_h, _j] = _d, _s, _p
    ROLL_N[_h] = len(_vert)


def _aktionen(d, s):
    """Mögliche (gehalten h, gedrehte Einsen t) nach Wurf d mit s neuen Sechsen; je h das kleinste t."""
    beste = {}
    for t in range(3):
        if t and s < t + 1:
            continue
        pool = list(d)
        for _ in range(t + 1 if t else 0):
            pool.remove(6)
        for groesse in range(3 - t):
            for k in set(combinations(sorted(pool), groesse)):
                h = H_ID[tuple(sorted(k + (1,) * t))]
                if h not in beste or t < beste[h]:
                    beste[h] = t
    return sorted(beste.items())


MAXA = 32
ACT_N = np.zeros((56, 4, 4), dtype=np.int64)
ACT_H = np.zeros((56, 4, 4, MAXA), dtype=np.int64)
ACT_T = np.zeros((56, 4, 4, MAXA), dtype=np.int64)
for _d, _t in enumerate(D_LISTE):
    for _m in range(1, 4):
        for _s in range(min(_m, _t.count(6)) + 1):
            _akt = _aktionen(_t, _s)
            assert len(_akt) <= MAXA
            ACT_N[_d, _m, _s] = len(_akt)
            for _j, (_h, _tt) in enumerate(_akt):
                ACT_H[_d, _m, _s, _j], ACT_T[_d, _m, _s, _j] = _h, _tt


def behalten_von(h: int, t: int) -> tuple:
    """Aus (gehalten h, gedreht t) die herausgelegten Würfel ohne gedrehte Einsen."""
    rest = list(H_LISTE[h])
    for _ in range(t):
        rest.remove(1)
    return tuple(rest)


# --------------------------------------------------------------------------- Baustein 1: Zug


@njit(cache=True)
def zug_dp(U_offen, U_verdeckt, grenze, darf_verdecken, verdeckt_modus):
    """Optimaler Zug, maximiert den Erwartungswert von U.

    darf_verdecken: Startspieler (darf jeden folgenden Wurf verdeckt werfen).
    verdeckt_modus: Nicht-Starter, dessen Wurf Nr. `grenze` zwingend verdeckt ist.
    Rückgabe: (Wert vor dem ersten Wurf, V[k, D, m, s], EV[k, h] = Wert eines offenen Wurfs k mit h gehalten).
    """
    V = np.zeros((4, 56, 4, 4))
    EV = np.zeros((5, NH))
    for k in range(grenze, 0, -1):
        rest = grenze - k
        for d in range(56):
            for m in range(1, 4):
                stopp = U_offen[W_VON[d, 1 if m == 3 else 0], k]
                for s in range(min(m, SECHSEN[d]) + 1):
                    best = stopp
                    if rest > 0:
                        for j in range(ACT_N[d, m, s]):
                            if ACT_T[d, m, s, j] > rest:
                                continue
                            h = ACT_H[d, m, s, j]
                            if darf_verdecken:
                                c = max(EV[k + 1, h], U_verdeckt[h, k + 1])
                            elif verdeckt_modus and k + 1 == grenze:
                                c = U_verdeckt[h, k + 1]
                            else:
                                c = EV[k + 1, h]
                            if c > best:
                                best = c
                    V[k, d, m, s] = best
        for h in range(NH):
            m = 3 - H_GROESSE[h]
            e = 0.0
            for j in range(ROLL_N[h]):
                e += ROLL_P[h, j] * V[k, ROLL_D[h, j], m, ROLL_S[h, j]]
            EV[k, h] = e
    if darf_verdecken:
        wert = max(EV[1, 0], U_verdeckt[0, 1])
    elif verdeckt_modus and grenze == 1:
        wert = U_verdeckt[0, 1]
    else:
        wert = EV[1, 0]
    return wert, V, EV


@njit(cache=True)
def wahl(V, EV, U_offen, U_verdeckt, grenze, darf_verdecken, verdeckt_modus, k, d, m, s):
    """Beste Entscheidung in Zustand (k, d, m, s). Rückgabe: (j, verdeckt); j = -1 heißt aufhören."""
    best = U_offen[W_VON[d, 1 if m == 3 else 0], k]
    best_j, best_v = -1, False
    rest = grenze - k
    if rest <= 0:
        return best_j, best_v
    for j in range(ACT_N[d, m, s]):
        if ACT_T[d, m, s, j] > rest:
            continue
        h = ACT_H[d, m, s, j]
        if darf_verdecken:
            if EV[k + 1, h] > best + 1e-12:
                best, best_j, best_v = EV[k + 1, h], j, False
            if U_verdeckt[h, k + 1] > best + 1e-12:
                best, best_j, best_v = U_verdeckt[h, k + 1], j, True
        elif verdeckt_modus and k + 1 == grenze:
            if U_verdeckt[h, k + 1] > best + 1e-12:
                best, best_j, best_v = U_verdeckt[h, k + 1], j, True
        elif EV[k + 1, h] > best + 1e-12:
            best, best_j, best_v = EV[k + 1, h], j, False
    return best_j, best_v


# --------------------------------------------------------------------------- Baustein 2: Runde zu zweit


@njit(cache=True)
def _ausgang(w1, k1, w2, k2, A, B):
    """Wert (P Startspieler verliert Spiel) für Ergebnis Starter (w1,k1) gegen Folger (w2,k2)."""
    if RANG_W[w2] > RANG_W[w1] or (RANG_W[w2] == RANG_W[w1] and k2 < k1):
        return A[DECK_W[w2]]  # Starter ist tief
    return B[DECK_W[w1]]  # Folger ist tief


@njit(cache=True)
def folger_bewertung(p1, k1, A, B, verdeckt_modus):
    """Bewertung der Zug-Enden des Folgers, wenn das Starter-Ergebnis Verteilung p1 über W hat (k1 Würfe)."""
    U2_offen = np.zeros((W, 4))
    U2_verdeckt = np.zeros((NH, 4))
    for w2 in range(W):
        for k2 in range(1, k1 + 1):
            x = 0.0
            for w1 in range(W):
                if p1[w1] > 0.0:
                    x += p1[w1] * _ausgang(w1, k1, w2, k2, A, B)
            U2_offen[w2, k2] = x
    if verdeckt_modus:
        for h2 in range(NH):
            x = 0.0
            for w2 in range(W):
                x += P_VERDECKT[h2, w2] * U2_offen[w2, k1]
            U2_verdeckt[h2, k1] = x
    return U2_offen, U2_verdeckt


@njit(cache=True)
def starter_bewertung(A, B):
    """Bewertung der Zug-Enden des Startspielers (als -P(Starter verliert), also zu maximieren)."""
    U1_offen = np.zeros((W, 4))
    U1_verdeckt = np.zeros((NH, 4))
    p1 = np.zeros(W)
    for k1 in range(1, 4):
        for w1 in range(W):
            p1[:] = 0.0
            p1[w1] = 1.0
            U2o, U2v = folger_bewertung(p1, k1, A, B, False)
            wert, _, _ = zug_dp(U2o, U2v, k1, False, False)
            U1_offen[w1, k1] = -wert
        for h1 in range(1 if k1 == 1 else NH):
            U2o, U2v = folger_bewertung(P_VERDECKT[h1], k1, A, B, True)
            wert, _, _ = zug_dp(U2o, U2v, k1, False, True)
            U1_verdeckt[h1, k1] = -wert
    return U1_offen, U1_verdeckt


@njit(cache=True)
def runde2(A, B):
    """P(Startspieler verliert das Spiel) bei optimalem Spiel beider in dieser Runde.

    A[a]: P(Starter verliert Spiel), wenn der Starter a Deckel bekommt (a = 1..6, 7 = Schock Aus).
    B[a]: dasselbe, wenn der Folgespieler a Deckel bekommt.
    """
    U1o, U1v = starter_bewertung(A, B)
    wert, _, _ = zug_dp(U1o, U1v, 3, True, False)
    return -wert


# --------------------------------------------------------------------------- Baustein 3: Spiel zu zweit

GESAMT = 13


@dataclass
class Haelfte2:
    """Lösung einer Hälfte zu zweit. X[(mitte, d0, starter)] = P(Spieler 0 verliert das Spiel)."""

    t0: float  # Wert, wenn Spieler 0 die Hälfte verliert
    t1: float
    X: dict

    def wert(self, mitte, d0, starter):
        d1 = GESAMT - mitte - d0
        if d0 == GESAMT:
            return self.t0
        if d1 == GESAMT:
            return self.t1
        return self.X[(mitte, d0, starter)]

    def nach_transfer(self, mitte, d0, empfaenger, a):
        """Wert nach der Runde, wenn `empfaenger` a Deckel bekommt (a = 7: Schock Aus)."""
        if a == AUS:
            return self.t0 if empfaenger == 0 else self.t1
        d = [d0, GESAMT - mitte - d0]
        if mitte > 0:
            x = min(a, mitte)
            mitte -= x
        else:
            x = min(a, d[1 - empfaenger])
            d[1 - empfaenger] -= x
        d[empfaenger] += x
        # Nächster Startspieler: Verlierer der Runde; bei leerer Mitte der mit den meisten Deckeln
        starter = empfaenger if mitte > 0 else (0 if d[0] > d[1] else 1)
        return self.wert(mitte, d[0], starter)

    def AB(self, mitte, d0, starter):
        """A, B aus Sicht des Starters (P Starter verliert Spiel) für runde2."""
        A, B = np.zeros(8), np.zeros(8)
        for a in range(1, 8):
            xa = self.nach_transfer(mitte, d0, starter, a)
            xb = self.nach_transfer(mitte, d0, 1 - starter, a)
            A[a], B[a] = (xa, xb) if starter == 0 else (1 - xa, 1 - xb)
        return A, B


def loese_haelfte2(t0, t1, toleranz=1e-12, max_iter=10_000):
    h = Haelfte2(t0, t1, {})
    zustaende = [(m, d0, s) for m in range(GESAMT + 1) for d0 in range(GESAMT - m + 1) for s in (0, 1)
                 if d0 < GESAMT and GESAMT - m - d0 < GESAMT]
    for m in range(GESAMT + 1):
        schicht = [z for z in zustaende if z[0] == m]
        for z in schicht:
            h.X[z] = 0.5
        # mitte > 0: Übergänge nur in kleinere Mitte -> ein Durchgang reicht; mitte = 0: iterieren
        for _ in range(max_iter if m == 0 else 1):
            delta = 0.0
            for z in schicht:
                mitte, d0, s = z
                A, B = h.AB(mitte, d0, s)
                ps = runde2(A, B)
                neu = ps if s == 0 else 1 - ps
                delta = max(delta, abs(neu - h.X[z]))
                h.X[z] = neu
            if delta < toleranz:
                break
    return h


@dataclass
class Spiel2:
    finale: Haelfte2
    h2: dict  # Verlierer Hälfte 1 -> Haelfte2
    h1: Haelfte2

    def haelfte(self, name, haelften_verlierer):
        if name == "Finale":
            return self.finale
        if name == "Hälfte 2":
            return self.h2[haelften_verlierer[0]]
        return self.h1

    def p_verlust(self, starter):
        """P(Spieler 0 verliert das Spiel), wenn `starter` das Spiel beginnt."""
        return self.h1.wert(GESAMT, 0, starter)


def loese_spiel2():
    finale = loese_haelfte2(1.0, 0.0)
    h2 = {}
    for l1 in (0, 1):
        # Verliert l1 auch Hälfte 2: Spiel verloren; sonst Finale, das der Verlierer von Hälfte 2 beginnt
        t0 = 1.0 if l1 == 0 else finale.wert(GESAMT, 0, 0)
        t1 = 0.0 if l1 == 1 else finale.wert(GESAMT, 0, 1)
        h2[l1] = loese_haelfte2(t0, t1)
    h1 = loese_haelfte2(h2[0].wert(GESAMT, 0, 0), h2[1].wert(GESAMT, 0, 1))
    return Spiel2(finale, h2, h1)
