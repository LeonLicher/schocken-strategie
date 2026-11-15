"""Konter für 3 bis 6 Spieler (Näherung): jede Runde exakt, die Zukunft wie Stammtisch bewertet.

1. Ausgangsverteilung einer Runde mit n unabhängigen Spielern: P[h, menge, t] = P(Position h ist hoch mit
   dieser Deckelmenge, Position t ist tief). Für jedes Paar (h, t) gilt
       P = Σ_{x>y} p_h(x) p_t(y) Π_{o≠h,t} (G_o(x) − G_o(y)),   G_o(z) = P(Score_o < z)
   Das Produkt wird über alle Teilmengen ausmultipliziert; jeder Summand lässt sich mit einer Präfixsumme
   über y in linearer Zeit auswerten.
2. V0[zustand] = P(ich verliere das Spiel), wenn alle (auch ich) ab jetzt Stammtisch spielen. Weil
   Stammtisch nicht auf den Spielstand reagiert, ist die Ausgangsverteilung je Runde vom Spielstand
   unabhängig; V0 ist ein einfaches lineares Gleichungssystem. Im Finale (zu zweit) spielt der Bot den
   exakten Konter, deshalb kommen die Finalwerte aus konter2.
3. Der Bot entscheidet jede Runde exakt (zug_dp) mit Bewertung E[V0(nächster Zustand)].
"""

import itertools
import pickle
from pathlib import Path

import numpy as np
from numba import njit

from .engine import STOPP, Aktion, Sicht, Strategie
from .konter import F_FOLGER, S_START, lade_konter
from .loeser import (ACT_H, ACT_T, AUS, D_ID, DECK_W, GESAMT, H_ID, NH, P_VERDECKT, RANG_W, W, _W_ID,
                     behalten_von, wahl, zug_dp)

ERGEBNISSE = Path(__file__).resolve().parent.parent / "ergebnisse"
MAXN = 6


@njit(cache=True)
def _score(w, k, pos):
    return RANG_W[w] * 100 + (3 - k) * 10 + (9 - pos)


@njit(cache=True)
def ausgang_verteilung(n, D):
    """D[pos, w, k]: unabhängige Ergebnisverteilungen. Rückgabe P[h_pos, menge, t_pos]."""
    # gemeinsames, aufsteigend sortiertes Score-Gitter aller Positionen
    G = n * W * 3
    gsc = np.zeros(G, dtype=np.int64)
    gpos = np.zeros(G, dtype=np.int64)
    gam = np.zeros(G, dtype=np.int64)
    gp = np.zeros(G)
    c = 0
    for pos in range(n):
        for k in range(1, 4):
            for w in range(W):
                gsc[c], gpos[c], gam[c], gp[c] = _score(w, k, pos), pos, DECK_W[w], D[pos, w, k]
                c += 1
    ordnung = np.argsort(gsc)
    gsc, gpos, gam, gp = gsc[ordnung], gpos[ordnung], gam[ordnung], gp[ordnung]
    # Gl[o, g] = P(Score_o < gsc[g])
    Gl = np.zeros((n, G))
    lauf = np.zeros(n)
    for g in range(G):
        for o in range(n):
            Gl[o, g] = lauf[o]
        lauf[gpos[g]] += gp[g]
    P = np.zeros((n, 8, n))
    andere = np.zeros(MAXN, dtype=np.int64)
    for h in range(n):
        for t in range(n):
            if h == t:
                continue
            m = 0
            for o in range(n):
                if o != h and o != t:
                    andere[m] = o
                    m += 1
            for maske in range(1 << m):
                praefix = 0.0  # Σ_{y < x} p_t(y) Π_{o∉T} (−G_o(y))
                for g in range(G):
                    pos = gpos[g]
                    if pos == h and gp[g] > 0.0:
                        fx = 1.0
                        for i in range(m):
                            if maske >> i & 1:
                                fx *= Gl[andere[i], g]
                        P[h, gam[g], t] += gp[g] * fx * praefix
                    if pos == t and gp[g] > 0.0:
                        fy = 1.0
                        for i in range(m):
                            if not (maske >> i & 1):
                                fy *= -Gl[andere[i], g]
                        praefix += gp[g] * fy
    return P


def stammtisch_runde(n):
    """Ausgangsverteilung einer Runde mit n Stammtisch-Spielern (Position 0 = Startspieler)."""
    P = np.zeros((n, 8, n))
    for k1 in (1, 2, 3):
        D = np.zeros((n, W, 4))
        D[0, :, k1] = S_START[:, k1]
        for pos in range(1, n):
            D[pos] = F_FOLGER[k1]
        P += ausgang_verteilung(n, D)
    return P


# --------------------------------------------------------------------------- V0: alle spielen Stammtisch


class Stammtischwerte:
    """V0[phase][(mitte, deckel, starter)] = P(Sitz 0 verliert das Spiel), alle spielen Stammtisch;
    im Finale spielt Sitz 0 exakt Konter (Werte aus konter2)."""

    def __init__(self, n, zwei):
        self.n = n
        self.zwei = zwei
        self.runde = {k: stammtisch_runde(k) for k in range(2, n + 1)}
        self.V = {}

    def phasen(self):
        return [("H2", l1) for l1 in range(self.n)] + ["H1"]

    def endwert(self, phase, t):
        if phase == "H1":
            return self.wert(("H2", t), GESAMT, (0,) * self.n, t)
        l1 = phase[1]
        if t == l1:
            return 1.0 if l1 == 0 else 0.0
        if 0 not in (l1, t):
            return 0.0
        return self.zwei.wert("F", GESAMT, (0, 0), 0 if t == 0 else 1)

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
        kand = [i for i in range(self.n) if d[i] == meiste]
        return sum(self.wert(phase, 0, d, c) for c in kand) / len(kand)

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
                yield from ((mitte, deckel, s) for s in range(self.n) if deckel[s] == meiste)
            else:
                yield from ((mitte, deckel, s) for s in range(self.n))

    def bewerte(self, phase, z):
        mitte, deckel, starter = z
        reihe = self.reihenfolge(mitte, deckel, starter)
        P = self.runde[len(reihe)]
        Vn = self.vnext(phase, mitte, deckel)
        x = 0.0
        for h, a, t in zip(*np.nonzero(P)):
            x += P[h, a, t] * Vn[reihe[h], a, reihe[t]]
        return x

    def loese(self, melde=print, toleranz=1e-10):
        for phase in self.phasen():
            self.V[phase] = {}
            for mitte in range(GESAMT + 1):
                schicht = list(self.zustaende(mitte))
                for z in schicht:
                    self.V[phase][z] = 1.0 / self.n
                for _ in range(10000 if mitte == 0 else 1):
                    delta = 0.0
                    for z in schicht:
                        neu = self.bewerte(phase, z)
                        delta = max(delta, abs(neu - self.V[phase][z]))
                        self.V[phase][z] = neu
                    if delta < toleranz:
                        break
            melde(f"  {phase} fertig")
        return self


def datei(n):
    return ERGEBNISSE / f"stammtischwerte{n}.pkl"


def lade_werte(n):
    with open(datei(n), "rb") as f:
        return pickle.load(f)


# --------------------------------------------------------------------------- Bot


@njit(cache=True)
def _erwartung_n(n, D, Vn_aktiv):
    P = ausgang_verteilung(n, D)
    x = 0.0
    for h in range(n):
        for a in range(1, 8):
            for t in range(n):
                if P[h, a, t] != 0.0:
                    x += P[h, a, t] * Vn_aktiv[h, a, t]
    return x


@njit(cache=True)
def bewertung_runde(n, p, D_vor, k_grenze, ist_starter, verdeckt_modus, Vn_aktiv):
    """Uo, Uv (= -P(ich verliere)) für mich an Position p; vor mir D_vor, nach mir Stammtisch."""
    Uo = np.zeros((W, 4))
    Uv = np.zeros((NH, 4))
    D = np.zeros((n, W, 4))
    for pos in range(p):
        D[pos] = D_vor[pos]
    for k in range(1, (3 if ist_starter else k_grenze) + 1):
        L = k if ist_starter else k_grenze
        for pos in range(p + 1, n):
            D[pos] = F_FOLGER[L]
        for w in range(W):
            D[p, :, :] = 0.0
            D[p, w, k] = 1.0
            Uo[w, k] = -_erwartung_n(n, D, Vn_aktiv)
        if ist_starter or (verdeckt_modus and k == k_grenze):
            for h in range(NH):
                x = 0.0
                for w in range(W):
                    x += P_VERDECKT[h, w] * Uo[w, k]
                Uv[h, k] = x
    return Uo, Uv


class KonterNaeherung(Strategie):
    """Konter für 3 bis 6 Spieler (Näherung); im Finale exakter Konter."""

    name = "Konter"

    def __init__(self, werte=None, konter2=None):
        self.werte = werte or {}
        self.konter2 = konter2

    def _werte(self, n):
        if n not in self.werte:
            self.werte[n] = lade_werte(n)
        return self.werte[n]

    def tabellen(self, sicht: Sicht):
        alle = [p for p, _ in sicht.deckel]
        n = len(alle)
        if n == 2:
            from .konter import Konter
            return Konter({2: self.konter2 or lade_konter(2)}).tabellen(sicht)
        ich = sicht.spieler
        rel = {p: (alle.index(p) - alle.index(ich)) % n for p in alle}
        deckel = [0] * n
        for p, d in sicht.deckel:
            deckel[rel[p]] = d
        L = self._werte(n)
        phase = ("H2", rel[sicht.haelften_verlierer[0]]) if sicht.haelfte == "Hälfte 2" else "H1"
        Vn = L.vnext(phase, sicht.mitte, tuple(deckel))
        starter = ich if sicht.ist_starter else sicht.bisher[0].spieler
        reihe = L.reihenfolge(sicht.mitte, deckel, rel[starter])
        na = len(reihe)
        Vn_aktiv = np.zeros((na, 8, na))
        for i in range(na):
            for j in range(na):
                Vn_aktiv[i, :, j] = Vn[reihe[i], :, reihe[j]]
        D_vor = np.zeros((na, W, 4))
        for pos, e in enumerate(sicht.bisher):
            if e.verdeckt:
                D_vor[pos, :, e.wuerfe] = P_VERDECKT[H_ID[tuple(sorted(e.sichtbar))]]
            else:
                D_vor[pos, _W_ID[e.wertung], e.wuerfe] = 1.0
        Uo, Uv = bewertung_runde(na, sicht.position, D_vor, sicht.grenze, sicht.ist_starter,
                                 sicht.verdeckt_modus, Vn_aktiv)
        if sicht.ist_starter:
            return Uo, Uv, 3, True, False
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
