"""Konter: beste Antwort auf Stammtisch-Gegner (exakt, 2 und 3 Spieler).

Ich bin Sitz 0, alle anderen spielen nach `bots.stammtisch_entscheidung`. Diese Gegner schauen nicht auf
die Ergebnisse der anderen und verdecken nie. Ihr Endergebnis hängt deshalb nur von der Wurfgrenze ab:
  S[w, k]     Verteilung des Endergebnisses eines Stammtisch-Startspielers
  F[L, w, k]  Verteilung eines Stammtisch-Folgespielers bei Wurfgrenze L
(Ein erzwungen verdeckter letzter Wurf ändert daran nichts, weil danach nicht mehr entschieden wird.)

Wertiteration über alle Spielstände (Hälfte 1, Hälfte 2, Finale) wie in loeser.py. Im Zustand wird
meine Verlustwahrscheinlichkeit V gespeichert; in jeder Runde spiele ich per zug_dp optimal.
"""

import itertools
import pickle
from collections import defaultdict
from pathlib import Path

import numpy as np
from numba import njit, prange

from .bots import stammtisch_entscheidung
from .engine import STOPP, Aktion, Sicht, Strategie
from .loeser import (ACT_H, ACT_T, AUS, D_ID, DECK_W, GESAMT, H_ID, NH, P_VERDECKT, RANG_W, W, _W_ID,
                     behalten_von, wahl, zug_dp)
from .wertung import bewerte

ERGEBNISSE = Path(__file__).resolve().parent.parent / "ergebnisse"

# --------------------------------------------------------------------------- Stammtisch-Verteilungen


def stammtisch_verteilung(grenze, ist_starter):
    """Exakte Verteilung des Endergebnisses (w, k) eines Stammtisch-Spielers."""
    P = np.zeros((W, 4))
    front = {(): 1.0}
    for k in range(1, grenze + 1):
        neu_front = defaultdict(float)
        for gehalten, ph in front.items():
            r = 3 - len(gehalten)
            for wurf in itertools.product(range(1, 7), repeat=r):
                p = ph / 6 ** r
                wuerfel = gehalten + wurf
                w = _W_ID[bewerte(wuerfel, r == 3)]
                if k == grenze:
                    P[w, k] += p
                    continue
                e = stammtisch_entscheidung(k, wuerfel, wurf, grenze, ist_starter)
                if e is None:
                    P[w, k] += p
                else:
                    neu_front[tuple(sorted(e[0] + (1,) * e[1]))] += p
        front = neu_front
    return P


S_START = stammtisch_verteilung(3, True)
F_FOLGER = np.zeros((4, W, 4))
for _L in (1, 2, 3):
    F_FOLGER[_L] = stammtisch_verteilung(_L, False)

# --------------------------------------------------------------------------- Runden-Kerne (numba)


@njit(cache=True)
def _score(w, k, pos):
    """Größer = besser: Rang, dann weniger Würfe, dann frühere Position."""
    return RANG_W[w] * 100 + (3 - k) * 10 + (9 - pos)


@njit(cache=True)
def _ausgang(n, sc, am, sz, Vnext):
    """Wert für Spieler mit Scores sc, Deckelmengen am (des eigenen Wurfs) und Sitzen sz."""
    h, t = 0, 0
    for i in range(1, n):
        if sc[i] > sc[h]:
            h = i
        if sc[i] < sc[t]:
            t = i
    return Vnext[sz[h], am[h], sz[t]]


@njit(cache=True)
def erwartung(n, seats, D, Vnext):
    """E[Vnext] bei unabhängigen Ergebnissen; D[pos, w, k] = Verteilung des Spielers an Position pos."""
    sw = np.zeros((3, W * 3), dtype=np.int64)
    sk = np.zeros((3, W * 3), dtype=np.int64)
    sp = np.zeros((3, W * 3))
    ln = np.ones(3, dtype=np.int64)
    for pos in range(n):
        c = 0
        for k in range(1, 4):
            for w in range(W):
                if D[pos, w, k] > 0.0:
                    sw[pos, c], sk[pos, c], sp[pos, c] = w, k, D[pos, w, k]
                    c += 1
        ln[pos] = c
    sc = np.zeros(3, dtype=np.int64)
    am = np.zeros(3, dtype=np.int64)
    sz = np.zeros(3, dtype=np.int64)
    for pos in range(n):
        sz[pos] = seats[pos]
    tot = 0.0
    for i0 in range(ln[0]):
        sc[0], am[0] = _score(sw[0, i0], sk[0, i0], 0), DECK_W[sw[0, i0]]
        for i1 in range(ln[1] if n > 1 else 1):
            p01 = sp[0, i0]
            if n > 1:
                sc[1], am[1] = _score(sw[1, i1], sk[1, i1], 1), DECK_W[sw[1, i1]]
                p01 *= sp[1, i1]
            for i2 in range(ln[2] if n > 2 else 1):
                p = p01
                if n > 2:
                    sc[2], am[2] = _score(sw[2, i2], sk[2, i2], 2), DECK_W[sw[2, i2]]
                    p *= sp[2, i2]
                tot += p * _ausgang(n, sc, am, sz, Vnext)
    return tot


@njit(cache=True)
def _starter_bewertung(n, seats, F, Vnext):
    """Ich bin Startspieler: Bewertung meiner Zug-Enden (= -P(ich verliere))."""
    Uo = np.zeros((W, 4))
    Uv = np.zeros((NH, 4))
    D = np.zeros((3, W, 4))
    for k in range(1, 4):
        for pos in range(1, n):
            D[pos] = F[k]
        for w in range(W):
            D[0, :, :] = 0.0
            D[0, w, k] = 1.0
            Uo[w, k] = -erwartung(n, seats, D, Vnext)
        for h in range(NH):
            x = 0.0
            for w in range(W):
                x += P_VERDECKT[h, w] * Uo[w, k]
            Uv[h, k] = x
    return Uo, Uv


@njit(cache=True)
def wert_als_starter(n, seats, F, Vnext):
    Uo, Uv = _starter_bewertung(n, seats, F, Vnext)
    wert, _, _ = zug_dp(Uo, Uv, 3, True, False)
    return -wert


@njit(cache=True)
def wert_ohne_mich(n, seats, S, F, Vnext):
    D = np.zeros((3, W, 4))
    tot = 0.0
    for k1 in range(1, 4):
        D[0, :, :] = 0.0
        D[0, :, k1] = S[:, k1]
        for pos in range(1, n):
            D[pos] = F[k1]
        tot += erwartung(n, seats, D, Vnext)
    return tot


@njit(cache=True)
def wert_als_zweiter_von_drei(seats, S, F, Vnext):
    """n = 3, ich an Position 1: Startspieler bekannt, Spieler an Position 2 zufällig."""
    tot = 0.0
    D = np.zeros((3, W, 4))
    Uv = np.zeros((NH, 4))
    for k1 in range(1, 4):
        D[2] = F[k1]
        for w1 in range(W):
            p1 = S[w1, k1]
            if p1 == 0.0:
                continue
            D[0, :, :] = 0.0
            D[0, w1, k1] = 1.0
            Uo = np.zeros((W, 4))
            for k in range(1, k1 + 1):
                for w in range(W):
                    D[1, :, :] = 0.0
                    D[1, w, k] = 1.0
                    Uo[w, k] = -erwartung(3, seats, D, Vnext)
            wert, _, _ = zug_dp(Uo, Uv, k1, False, False)
            tot += p1 * (-wert)
    return tot


@njit(cache=True, parallel=True)
def wert_als_letzter(n, seats, S, F, Vnext):
    """Ich bin der letzte von n (2 oder 3): alle Ergebnisse vor mir sind bekannt."""
    # Liste aller Vorgeschichten (w1, k1, w2, k2, p)
    anz = 0
    for k1 in range(1, 4):
        for w1 in range(W):
            if S[w1, k1] > 0.0:
                if n == 2:
                    anz += 1
                else:
                    for k2 in range(1, k1 + 1):
                        for w2 in range(W):
                            if F[k1, w2, k2] > 0.0:
                                anz += 1
    hw1 = np.zeros(anz, dtype=np.int64)
    hk1 = np.zeros(anz, dtype=np.int64)
    hw2 = np.zeros(anz, dtype=np.int64)
    hk2 = np.zeros(anz, dtype=np.int64)
    hp = np.zeros(anz)
    c = 0
    for k1 in range(1, 4):
        for w1 in range(W):
            if S[w1, k1] > 0.0:
                if n == 2:
                    hw1[c], hk1[c], hp[c] = w1, k1, S[w1, k1]
                    c += 1
                else:
                    for k2 in range(1, k1 + 1):
                        for w2 in range(W):
                            if F[k1, w2, k2] > 0.0:
                                hw1[c], hk1[c], hw2[c], hk2[c] = w1, k1, w2, k2
                                hp[c] = S[w1, k1] * F[k1, w2, k2]
                                c += 1
    beitraege = np.zeros(anz)
    for i in prange(anz):
        sc = np.zeros(3, dtype=np.int64)
        am = np.zeros(3, dtype=np.int64)
        sz = np.zeros(3, dtype=np.int64)
        for pos in range(n):
            sz[pos] = seats[pos]
        k1 = hk1[i]
        sc[0], am[0] = _score(hw1[i], k1, 0), DECK_W[hw1[i]]
        if n == 3:
            sc[1], am[1] = _score(hw2[i], hk2[i], 1), DECK_W[hw2[i]]
        Uo = np.zeros((W, 4))
        Uv = np.zeros((NH, 4))
        for k in range(1, k1 + 1):
            for w in range(W):
                sc[n - 1], am[n - 1] = _score(w, k, n - 1), DECK_W[w]
                Uo[w, k] = -_ausgang(n, sc, am, sz, Vnext)
        wert, _, _ = zug_dp(Uo, Uv, k1, False, False)
        beitraege[i] = hp[i] * (-wert)
    return beitraege.sum()


@njit(cache=True)
def folger_bewertung_allgemein(n, seats, p, D_vor, k1, F, Vnext, verdeckt_modus):
    """Für den Bot: ich an Position p, Ergebnisse vor mir als Verteilungen D_vor[pos] (offen = Einheitsvektor,
    verdeckt = Mischung), Spieler nach mir Stammtisch mit Grenze k1. Rückgabe Uo, Uv (= -P(ich verliere))."""
    D = np.zeros((3, W, 4))
    for pos in range(p):
        D[pos] = D_vor[pos]
    for pos in range(p + 1, n):
        D[pos] = F[k1]
    Uo = np.zeros((W, 4))
    Uv = np.zeros((NH, 4))
    for k in range(1, k1 + 1):
        for w in range(W):
            D[p, :, :] = 0.0
            D[p, w, k] = 1.0
            Uo[w, k] = -erwartung(n, seats, D, Vnext)
    if verdeckt_modus:
        for h in range(NH):
            x = 0.0
            for w in range(W):
                x += P_VERDECKT[h, w] * Uo[w, k1]
            Uv[h, k1] = x
    return Uo, Uv


def wert_runde(n, seats, p):
    """Wählt den passenden Kern. p = meine Position (-1: ich spiele nicht mit)."""
    if p == -1:
        return lambda V: wert_ohne_mich(n, seats, S_START, F_FOLGER, V)
    if p == 0:
        return lambda V: wert_als_starter(n, seats, F_FOLGER, V)
    if p == n - 1:
        return lambda V: wert_als_letzter(n, seats, S_START, F_FOLGER, V)
    return lambda V: wert_als_zweiter_von_drei(seats, S_START, F_FOLGER, V)


# --------------------------------------------------------------------------- Spielstände und Wertiteration


class KonterLoesung:
    """V[phase][(mitte, deckel, starter)] = P(ich, Sitz 0, verliere das Spiel) bei Konter gegen Stammtisch.

    Phasen: "H1", ("H2", l1) und bei 2 Spielern "F". Bei 3 Spielern ist das Finale ein 2-Spieler-Spiel
    und kommt aus der 2-Spieler-Lösung (`zwei`).
    """

    def __init__(self, n, zwei=None):
        self.n = n
        self.zwei = zwei
        self.V = {}

    # --- Phasen
    def phasen(self):
        ph = [("H2", l1) for l1 in range(self.n)] + ["H1"]
        return (["F"] + ph) if self.n == 2 else ph

    def endwert(self, phase, verlierer):
        """Wert, wenn `verlierer` die Hälfte der Phase verliert."""
        if phase == "F":
            return 1.0 if verlierer == 0 else 0.0
        if phase == "H1":
            return self.wert(("H2", verlierer), GESAMT, (0,) * self.n, verlierer)
        l1 = phase[1]
        if verlierer == l1:
            return 1.0 if l1 == 0 else 0.0
        if 0 not in (l1, verlierer):
            return 0.0
        # Finale zwischen mir und einem Stammtisch-Spieler, es beginnt der Verlierer von Hälfte 2
        if self.n == 2:
            return self.wert("F", GESAMT, (0, 0), verlierer)
        return self.zwei.wert("F", GESAMT, (0, 0), 0 if verlierer == 0 else 1)

    def wert(self, phase, mitte, deckel, starter):
        for i, d in enumerate(deckel):
            if d >= GESAMT:
                return self.endwert(phase, i)
        return self.V[phase][(mitte, tuple(deckel), starter)]

    def nach_runde(self, phase, mitte, deckel, h, a, t):
        if a == AUS:
            return self.endwert(phase, t)
        d = list(deckel)
        if mitte > 0:
            x = min(a, mitte)
            mitte -= x
        else:
            x = min(a, d[h])
            d[h] -= x
        d[t] += x
        if d[t] >= GESAMT:
            return self.endwert(phase, t)
        if mitte > 0:
            return self.wert(phase, mitte, d, t)
        meiste = max(d)
        kandidaten = [i for i in range(self.n) if d[i] == meiste]
        return sum(self.wert(phase, 0, d, c) for c in kandidaten) / len(kandidaten)

    def vnext(self, phase, mitte, deckel):
        V = np.zeros((self.n, 8, self.n))
        for h in range(self.n):
            for t in range(self.n):
                if h != t:
                    for a in range(1, 8):
                        V[h, a, t] = self.nach_runde(phase, mitte, deckel, h, a, t)
        return V

    def reihenfolge(self, mitte, deckel, starter):
        aktiv = list(range(self.n)) if mitte > 0 else [i for i in range(self.n) if deckel[i] > 0]
        i = aktiv.index(starter)
        return aktiv[i:] + aktiv[:i]

    def zustaende(self, mitte):
        for deckel in itertools.product(range(GESAMT), repeat=self.n):
            if sum(deckel) != GESAMT - mitte:
                continue
            if mitte == 0:
                meiste = max(deckel)
                starter_liste = [i for i in range(self.n) if deckel[i] == meiste]
            else:
                starter_liste = range(self.n)
            for s in starter_liste:
                yield (mitte, deckel, s)

    def bewerte_zustand(self, phase, z):
        mitte, deckel, starter = z
        reihe = self.reihenfolge(mitte, deckel, starter)
        p = reihe.index(0) if 0 in reihe else -1
        seats = np.array(reihe + [0] * (3 - len(reihe)), dtype=np.int64)
        return wert_runde(len(reihe), seats, p)(self.vnext(phase, mitte, deckel))

    def loese_phase(self, phase, toleranz=1e-9, melde=print):
        self.V[phase] = {}
        for mitte in range(GESAMT + 1):
            schicht = list(self.zustaende(mitte))
            for z in schicht:
                self.V[phase][z] = 0.5
            for it in range(1000 if mitte == 0 else 1):
                delta = 0.0
                for z in schicht:
                    neu = self.bewerte_zustand(phase, z)
                    delta = max(delta, abs(neu - self.V[phase][z]))
                    self.V[phase][z] = neu
                if mitte == 0:
                    melde(f"    {phase} Mitte 0, Iteration {it + 1}: Änderung {delta:.2e}")
                if delta < toleranz:
                    break
            melde(f"  {phase}: Mitte {mitte} fertig ({len(schicht)} Zustände)")

    def loese(self, melde=print):
        for phase in self.phasen():
            self.loese_phase(phase, melde=melde)
        return self

    def p_verlust(self):
        """P(ich verliere das Spiel) bei zufälligem Spielbeginner."""
        return float(np.mean([self.wert("H1", GESAMT, (0,) * self.n, s) for s in range(self.n)]))


def datei(n):
    return ERGEBNISSE / f"konter{n}.pkl"


def lade_konter(n):
    with open(datei(n), "rb") as f:
        return pickle.load(f)


def speichere(loesung):
    ERGEBNISSE.mkdir(exist_ok=True)
    with open(datei(loesung.n), "wb") as f:
        pickle.dump(loesung, f)


# --------------------------------------------------------------------------- Bot


class Konter(Strategie):
    """Spielt die beste Antwort auf Stammtisch-Gegner (für 2 oder 3 Spieler gelöst)."""

    name = "Konter"

    def __init__(self, loesungen=None):
        self.loesungen = loesungen or {}

    def _loesung(self, n):
        if n not in self.loesungen:
            self.loesungen[n] = lade_konter(n)
        return self.loesungen[n]

    def tabellen(self, sicht: Sicht):
        """Zug-Tabellen für meine Entscheidung (Werte = -P(ich verliere))."""
        alle = [p for p, _ in sicht.deckel]
        n = len(alle)
        ich = sicht.spieler
        # Sitze relativ zu mir (ich = 0), im Uhrzeigersinn
        rel = {p: (alle.index(p) - alle.index(ich)) % n for p in alle}
        deckel = [0] * n
        for p, d in sicht.deckel:
            deckel[rel[p]] = d
        L = self._loesung(n)
        if sicht.haelfte == "Finale":
            phase = "F"
        elif sicht.haelfte == "Hälfte 2":
            phase = ("H2", rel[sicht.haelften_verlierer[0]])
        else:
            phase = "H1"
        Vn = L.vnext(phase, sicht.mitte, tuple(deckel))
        starter = ich if sicht.ist_starter else sicht.bisher[0].spieler
        reihe = L.reihenfolge(sicht.mitte, deckel, rel[starter])
        seats = np.array(reihe + [0] * (3 - len(reihe)), dtype=np.int64)
        if sicht.ist_starter:
            Uo, Uv = _starter_bewertung(len(reihe), seats, F_FOLGER, Vn)
            return Uo, Uv, 3, True, False
        D_vor = np.zeros((3, W, 4))
        for pos, e in enumerate(sicht.bisher):
            if e.verdeckt:
                D_vor[pos, :, e.wuerfe] = P_VERDECKT[H_ID[tuple(sorted(e.sichtbar))]]
            else:
                D_vor[pos, _W_ID[e.wertung], e.wuerfe] = 1.0
        Uo, Uv = folger_bewertung_allgemein(len(reihe), seats, sicht.position, D_vor, sicht.grenze,
                                            F_FOLGER, Vn, sicht.verdeckt_modus)
        return Uo, Uv, sicht.grenze, False, sicht.verdeckt_modus

    def entscheide(self, sicht: Sicht) -> Aktion:
        Uo, Uv, grenze, darf, vm = self.tabellen(sicht)
        _, V, EV = zug_dp(Uo, Uv, grenze, darf, vm)
        if sicht.phase == "vor_wurf":
            return Aktion(verdeckt=bool(Uv[0, 1] > EV[1, 0] + 1e-12))
        d = D_ID[tuple(sorted(sicht.wuerfel))]
        m, s = len(sicht.neu), sicht.neu.count(6)
        j, verdeckt = wahl(V, EV, Uo, Uv, grenze, darf, vm, sicht.wurf_nr, d, m, s)
        if j < 0:
            return STOPP
        h, t = ACT_H[d, m, s, j], ACT_T[d, m, s, j]
        return Aktion(behalten=behalten_von(h, t), drehen=int(t), verdeckt=bool(verdeckt))
