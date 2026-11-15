"""Echtes Optimum zu dritt: alle Spieler spielen perfekt (teilspielperfektes Gleichgewicht).

Jede Runde wird rückwärts gelöst: Der letzte Spieler antwortet optimal auf alles vor ihm, der mittlere
optimal unter Kenntnis dieser Antwort, der Startspieler optimal unter Kenntnis beider. Jeder minimiert die
eigene Wahrscheinlichkeit, das Spiel zu verlieren. Werte sind Vektoren: V[i] = P(Sitz i verliert das Spiel).

Ergebnisse vor einem Spieler sind offen (Wertung w) oder verdeckt (gehaltene Würfel h, Ergebnis zufällig).
Um Paare unabhängiger Ergebnisse schnell auszuwerten, wird eines aufgezählt und das andere über
Präfixsummen (nach Score sortiert) abgefragt.

Finale = 2-Spieler-Spiel, kommt aus loeser.loese_spiel2 (ergebnisse/loesung2.pkl).
"""

import itertools
import pickle
from pathlib import Path

import numpy as np
from numba import njit, prange

from .loeser import AUS, DECK_W, GESAMT, NH, P_VERDECKT, RANG_W, ROLL_D, ROLL_N, ROLL_P, ROLL_S, W, W_VON, \
    ACT_H, H_GROESSE, wahl, zug_dp

ERGEBNISSE = Path(__file__).resolve().parent.parent / "ergebnisse"
N = 3

# Liste der Zug-Enden des Startspielers: (art 0=offen/1=verdeckt, w oder h, k)
_T1 = [(0, w, k) for k in (1, 2, 3) for w in range(W)] + [(1, 0, 1)] + [(1, h, k) for k in (2, 3) for h in range(NH)]
T1_ART = np.array([t[0] for t in _T1], dtype=np.int64)
T1_X = np.array([t[1] for t in _T1], dtype=np.int64)
T1_K = np.array([t[2] for t in _T1], dtype=np.int64)
N_T1 = len(_T1)


@njit(cache=True)
def _score(w, k, pos):
    return RANG_W[w] * 100 + (3 - k) * 10 + (9 - pos)


# --------------------------------------------------------------------------- Verteilungen als sortierte Listen


@njit(cache=True)
def _dist(art, x, k, pos):
    """Ergebnis-Verteilung eines Zug-Endes, nach Score aufsteigend: (sc, am, p, n)."""
    sc = np.zeros(W, dtype=np.int64)
    am = np.zeros(W, dtype=np.int64)
    p = np.zeros(W)
    if art == 0:
        sc[0], am[0], p[0] = _score(x, k, pos), DECK_W[x], 1.0
        return sc, am, p, 1
    n = 0
    for w in range(W):  # W ist nach Rang sortiert -> Scores aufsteigend
        if P_VERDECKT[x, w] > 0.0:
            sc[n], am[n], p[n] = _score(w, k, pos), DECK_W[w], P_VERDECKT[x, w]
            n += 1
    return sc, am, p, n


@njit(cache=True)
def _praefix(am, p, n):
    cum = np.zeros(n + 1)
    cum_am = np.zeros((8, n + 1))
    for j in range(n):
        cum[j + 1] = cum[j] + p[j]
        for a in range(8):
            cum_am[a, j + 1] = cum_am[a, j]
        cum_am[am[j], j + 1] += p[j]
    return cum, cum_am


@njit(cache=True)
def _erw_paar(x_sc, x_am, x_z, A_sc, A_am, A_p, A_n, A_z, B_sc, B_n, B_cum, B_cum_am, B_z, Vnext, out):
    """out += E[Vnext[hoch, menge, tief, :]] für mich (x) und zwei unabhängige Gegner A (aufgezählt) und B
    (über Präfixsummen)."""
    for i in range(A_n):
        pa = A_p[i]
        if A_sc[i] > x_sc:
            hi_sc, hi_am, hi_z, lo_sc, lo_z = A_sc[i], A_am[i], A_z, x_sc, x_z
        else:
            hi_sc, hi_am, hi_z, lo_sc, lo_z = x_sc, x_am, x_z, A_sc[i], A_z
        i_lo = np.searchsorted(B_sc[:B_n], lo_sc)
        i_hi = np.searchsorted(B_sc[:B_n], hi_sc)
        p_unten = B_cum[i_lo]
        p_mitte = B_cum[i_hi] - B_cum[i_lo]
        for c in range(N):
            v = p_unten * Vnext[hi_z, hi_am, B_z, c] + p_mitte * Vnext[hi_z, hi_am, lo_z, c]
            for a in range(1, 8):
                pb = B_cum_am[a, B_n] - B_cum_am[a, i_hi]
                if pb > 0.0:
                    v += pb * Vnext[B_z, a, lo_z, c]
            out[c] += pa * v


@njit(cache=True)
def _erw_einzel(x_sc, x_am, x_z, A_sc, A_am, A_p, A_n, A_z, Vnext, out):
    for i in range(A_n):
        if A_sc[i] > x_sc:
            for c in range(N):
                out[c] += A_p[i] * Vnext[A_z, A_am[i], x_z, c]
        else:
            for c in range(N):
                out[c] += A_p[i] * Vnext[x_z, x_am, A_z, c]


# --------------------------------------------------------------------------- Optimaler Zug + Verteilung der Zug-Enden


@njit(cache=True)
def verteilung(V, EV, Uo, Uv, grenze, darf, vm):
    """Verteilung der Zug-Enden (offen T_o[w,k], verdeckt T_v[h,k]) bei optimalem Spiel."""
    T_o = np.zeros((W, 4))
    T_v = np.zeros((NH, 4))
    if darf:
        if Uv[0, 1] > EV[1, 0] + 1e-12:
            T_v[0, 1] = 1.0
            return T_o, T_v
    elif vm and grenze == 1:
        T_v[0, 1] = 1.0
        return T_o, T_v
    front = np.zeros(NH)
    front[0] = 1.0
    for k in range(1, grenze + 1):
        neu = np.zeros(NH)
        for h in range(NH):
            if front[h] == 0.0:
                continue
            m = 3 - H_GROESSE[h]
            for j in range(ROLL_N[h]):
                d, s, p = ROLL_D[h, j], ROLL_S[h, j], front[h] * ROLL_P[h, j]
                adh = 1 if m == 3 else 0
                if k == grenze:
                    T_o[W_VON[d, adh], k] += p
                    continue
                jj, vv = wahl(V, EV, Uo, Uv, grenze, darf, vm, k, d, m, s)
                if jj < 0:
                    T_o[W_VON[d, adh], k] += p
                elif vv:
                    T_v[ACT_H[d, m, s, jj], k + 1] += p
                else:
                    neu[ACT_H[d, m, s, jj]] += p
        front = neu
    return T_o, T_v


@njit(cache=True)
def _spiele_zug(E_o, E_v, z, grenze, darf, vm):
    """Spieler auf Sitz z spielt optimal; E_o[w,k,:] / E_v[h,k,:] = Wertvektoren seiner Zug-Enden.
    Rückgabe: erwarteter Wertvektor."""
    Uo = np.zeros((W, 4))
    Uv = np.zeros((NH, 4))
    for w in range(W):
        for k in range(1, 4):
            Uo[w, k] = -E_o[w, k, z]
    for h in range(NH):
        for k in range(1, 4):
            Uv[h, k] = -E_v[h, k, z]
    _, V, EV = zug_dp(Uo, Uv, grenze, darf, vm)
    T_o, T_v = verteilung(V, EV, Uo, Uv, grenze, darf, vm)
    r = np.zeros(N)
    for w in range(W):
        for k in range(1, 4):
            if T_o[w, k] > 0.0:
                for c in range(N):
                    r[c] += T_o[w, k] * E_o[w, k, c]
    for h in range(NH):
        for k in range(1, 4):
            if T_v[h, k] > 0.0:
                for c in range(N):
                    r[c] += T_v[h, k] * E_v[h, k, c]
    return r


@njit(cache=True)
def _verdeckt_aus_offen(E_o, E_v, k):
    """E_v[h,k,:] = Mischung der offenen Werte bei Wurfzahl k gemäß verdecktem Wurf mit h gehalten."""
    for h in range(NH):
        for c in range(N):
            x = 0.0
            for w in range(W):
                x += P_VERDECKT[h, w] * E_o[w, k, c]
            E_v[h, k, c] = x


# --------------------------------------------------------------------------- Runde zu dritt


@njit(cache=True)
def _letzter(d1, d2, L, vm, z, Vnext):
    """Letzter Spieler (Position 2) gegen bekannte Verteilungen d1 (Pos. 0) und d2 (Pos. 1)."""
    (s1, a1, p1, n1), (s2, a2, p2, n2) = d1, d2
    if n1 <= n2:
        A_sc, A_am, A_p, A_n, A_z, B_sc, B_am, B_p, B_n, B_z = s1, a1, p1, n1, z[0], s2, a2, p2, n2, z[1]
    else:
        A_sc, A_am, A_p, A_n, A_z, B_sc, B_am, B_p, B_n, B_z = s2, a2, p2, n2, z[1], s1, a1, p1, n1, z[0]
    B_cum, B_cum_am = _praefix(B_am, B_p, B_n)
    E_o = np.zeros((W, 4, N))
    E_v = np.zeros((NH, 4, N))
    for k in range(1, L + 1):
        for w in range(W):
            _erw_paar(_score(w, k, 2), DECK_W[w], z[2], A_sc, A_am, A_p, A_n, A_z,
                      B_sc, B_n, B_cum, B_cum_am, B_z, Vnext, E_o[w, k])
    if vm:
        _verdeckt_aus_offen(E_o, E_v, L)
    return _spiele_zug(E_o, E_v, z[2], L, False, vm)


@njit(cache=True)
def _mitte(t, z, Vnext):
    """Mittlerer Spieler bei Startspieler-Ende t; Rückgabe: Wertvektor."""
    art, x, L = T1_ART[t], T1_X[t], T1_K[t]
    vm = art == 1
    d1 = _dist(art, x, L, 0)
    E_o = np.zeros((W, 4, N))
    E_v = np.zeros((NH, 4, N))
    for k2 in range(1, L + 1):
        if vm and k2 == L:
            continue
        for w2 in range(W):
            E_o[w2, k2] = _letzter(d1, _dist(0, w2, k2, 1), L, vm, z, Vnext)
    if vm:
        for h2 in range(1 if L == 1 else NH):
            E_v[h2, L] = _letzter(d1, _dist(1, h2, L, 1), L, vm, z, Vnext)
    return _spiele_zug(E_o, E_v, z[1], L, False, vm)


@njit(cache=True, parallel=True)
def runde3(z, Vnext):
    """Wertvektor einer Runde zu dritt (Sitze z[0..2] in Spielreihenfolge)."""
    Q = np.zeros((N_T1, N))
    for t in prange(N_T1):
        Q[t] = _mitte(t, z, Vnext)
    E_o = np.zeros((W, 4, N))
    E_v = np.zeros((NH, 4, N))
    for t in range(N_T1):
        if T1_ART[t] == 0:
            E_o[T1_X[t], T1_K[t]] = Q[t]
        else:
            E_v[T1_X[t], T1_K[t]] = Q[t]
    return _spiele_zug(E_o, E_v, z[0], 3, True, False)


@njit(cache=True)
def _letzter2(d1, L, vm, z, Vnext):
    s1, a1, p1, n1 = d1
    E_o = np.zeros((W, 4, N))
    E_v = np.zeros((NH, 4, N))
    for k in range(1, L + 1):
        for w in range(W):
            _erw_einzel(_score(w, k, 1), DECK_W[w], z[1], s1, a1, p1, n1, z[0], Vnext, E_o[w, k])
    if vm:
        _verdeckt_aus_offen(E_o, E_v, L)
    return _spiele_zug(E_o, E_v, z[1], L, False, vm)


@njit(cache=True)
def runde2(z, Vnext):
    """Wertvektor einer Runde zu zweit (ein Spieler ist ohne Deckel raus)."""
    E_o = np.zeros((W, 4, N))
    E_v = np.zeros((NH, 4, N))
    for t in range(N_T1):
        art, x, L = T1_ART[t], T1_X[t], T1_K[t]
        r = _letzter2(_dist(art, x, L, 0), L, art == 1, z, Vnext)
        if art == 0:
            E_o[x, L] = r
        else:
            E_v[x, L] = r
    return _spiele_zug(E_o, E_v, z[0], 3, True, False)


# --------------------------------------------------------------------------- Spielstände und Wertiteration


class Gleichgewicht3:
    """V[phase][(mitte, deckel, starter)] = Vektor P(Sitz i verliert das Spiel), alle spielen perfekt."""

    def __init__(self, zwei):
        self.zwei = zwei  # loeser.Spiel2 (für das Finale)
        self.V = {}

    def phasen(self):
        return [("H2", l1) for l1 in range(N)] + ["H1"]

    def endwert(self, phase, t):
        if phase == "H1":
            return self.wert(("H2", t), GESAMT, (0,) * N, t)
        l1 = phase[1]
        v = np.zeros(N)
        if t == l1:
            v[l1] = 1.0
        else:
            f0 = self.zwei.finale.wert(GESAMT, 0, 0)  # P(Startspieler des Finales verliert)
            v[t], v[l1] = f0, 1.0 - f0
        return v

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
        kandidaten = [i for i in range(N) if d[i] == meiste]
        return sum(self.wert(phase, 0, d, c) for c in kandidaten) / len(kandidaten)

    def vnext(self, phase, mitte, deckel):
        V = np.zeros((N, 8, N, N))
        for h in range(N):
            for t in range(N):
                if h != t:
                    for a in range(1, 8):
                        V[h, a, t] = self.nach_runde(phase, mitte, deckel, h, a, t)
        return V

    @staticmethod
    def reihenfolge(mitte, deckel, starter):
        aktiv = list(range(N)) if mitte > 0 else [i for i in range(N) if deckel[i] > 0]
        i = aktiv.index(starter)
        return aktiv[i:] + aktiv[:i]

    @staticmethod
    def zustaende(mitte):
        for deckel in itertools.product(range(GESAMT), repeat=N):
            if sum(deckel) != GESAMT - mitte:
                continue
            if mitte == 0:
                meiste = max(deckel)
                starter_liste = [i for i in range(N) if deckel[i] == meiste]
            else:
                starter_liste = range(N)
            for s in starter_liste:
                yield (mitte, deckel, s)

    def bewerte_zustand(self, phase, z):
        mitte, deckel, starter = z
        reihe = self.reihenfolge(mitte, deckel, starter)
        seats = np.array(reihe + [0] * (3 - len(reihe)), dtype=np.int64)
        Vn = self.vnext(phase, mitte, deckel)
        return runde3(seats, Vn) if len(reihe) == 3 else runde2(seats, Vn)

    def loese_phase(self, phase, toleranz=1e-8, melde=print):
        self.V[phase] = {}
        for mitte in range(GESAMT + 1):
            schicht = list(self.zustaende(mitte))
            for z in schicht:
                self.V[phase][z] = np.full(N, 1.0 / N)
            for it in range(500 if mitte == 0 else 1):
                delta = 0.0
                for z in schicht:
                    neu = self.bewerte_zustand(phase, z)
                    delta = max(delta, float(np.abs(neu - self.V[phase][z]).max()))
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

    def p_verlust(self, sitz=0):
        """P(Sitz verliert das Spiel) bei zufälligem Spielbeginner."""
        return float(np.mean([self.wert("H1", GESAMT, (0,) * N, s)[sitz] for s in range(N)]))


def datei():
    return ERGEBNISSE / "optimum3.pkl"


def lade_optimum3():
    with open(datei(), "rb") as f:
        return pickle.load(f)


def speichere(l):
    ERGEBNISSE.mkdir(exist_ok=True)
    with open(datei(), "wb") as f:
        pickle.dump(l, f)
