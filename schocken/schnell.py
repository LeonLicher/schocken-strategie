"""Schneller Simulator (Numba) für Strategien, die als Parameter-Vektor beschrieben sind.

Gleiche Regeln wie engine.py. Die Korrektheit wird statistisch gegen die Referenz-Engine geprüft
(tests/test_schnell.py). Strategie-Parameter je Spieler (int64-Zeile):

    [0] STARTER_KLASSE   Startspieler hört auf, sobald die Klasse >= diesem Wert ist
                         (0 Einfach, 1 Straße, 2 General, 3 Schock, 4 Schock Aus; 5 = nie vor dem 3. Wurf)
    [1] VERDECKT_WURF    Startspieler wirft diesen Wurf (1..3) verdeckt, 0 = nie
    [2] FOLGER_KLASSE    Nicht-Starter ohne offenen Vergleichswurf hört ab dieser Klasse auf
    [3] FOLGER_MARGE     Nicht-Starter hört auf, wenn sein Rang >= schlechtester offener Rang + Marge
                         (Marge 0 = knapp besser reicht; Rang wie wertung.Wertung.rang)
    [4] DREHEN           1 = Sechsen drehen, wenn erlaubt, 0 = nie
"""

import numpy as np
from numba import njit, prange

from .wertung import DECKEL_GESAMT, bewerte

STARTER_KLASSE, VERDECKT_WURF, FOLGER_KLASSE, FOLGER_MARGE, DREHEN = range(5)
N_PARAMS = 5

FAUSTREGEL = np.array([1, 0, 1, 0, 1], dtype=np.int64)

# Tabellen über alle 216 geordneten Würfe: code = (a-1)*36 + (b-1)*6 + (c-1)
RANG = np.zeros((216, 2), dtype=np.int64)
KLASSE = np.zeros((216, 2), dtype=np.int64)
DECKEL = np.zeros((216, 2), dtype=np.int64)
for _a in range(6):
    for _b in range(6):
        for _c in range(6):
            for _adh in range(2):
                _w = bewerte((_a + 1, _b + 1, _c + 1), bool(_adh))
                _code = _a * 36 + _b * 6 + _c
                RANG[_code, _adh] = _w.rang
                KLASSE[_code, _adh] = _w.klasse
                DECKEL[_code, _adh] = _w.deckel


@njit(cache=True)
def _schluessel(rang, wuerfe, position):
    # größer = besser; Gleichstand: weniger Würfe, dann frühere Position
    return rang * 100 + (3 - wuerfe) * 10 + (9 - position)


@njit(cache=True)
def _zug(p, ist_starter, grenze, verdeckt_modus, min_offen, gibt_offen, position, RANG, KLASSE):
    """Spielt einen Zug. Rückgabe: (schluessel, verdeckt, code, adh, wuerfe)."""
    d = np.zeros(3, dtype=np.int64)
    if ist_starter:
        grenze = 3
        verdeckt = p[VERDECKT_WURF] == 1
    else:
        verdeckt = verdeckt_modus and grenze == 1
    gehalten = 0
    wurf = 0
    while True:
        for i in range(gehalten, 3):
            d[i] = np.random.randint(1, 7)
        wurf += 1
        adh = 1 if gehalten == 0 else 0
        code = (d[0] - 1) * 36 + (d[1] - 1) * 6 + (d[2] - 1)
        if verdeckt or wurf >= grenze:
            break
        rang = RANG[code, adh]
        klasse = KLASSE[code, adh]
        # --- aufhören?
        if ist_starter:
            stopp = klasse >= p[STARTER_KLASSE]
        elif gibt_offen:
            stopp = _schluessel(rang, wurf, position) > min_offen and rang >= (min_offen // 100) + p[FOLGER_MARGE]
        else:
            stopp = klasse >= p[FOLGER_KLASSE]
        if stopp:
            break
        # --- weiterwürfeln: Einsen behalten, ggf. Sechsen drehen
        einsen = 0
        for i in range(3):
            if d[i] == 1:
                einsen += 1
        if einsen > 2:
            einsen = 2
        sechsen_neu = 0
        for i in range(gehalten, 3):
            if d[i] == 6:
                sechsen_neu += 1
        rest = grenze - wurf
        if p[DREHEN] == 1 and einsen == 0 and sechsen_neu >= 3 and rest >= 2:
            neu_gehalten = 2
        elif p[DREHEN] == 1 and einsen < 2 and sechsen_neu >= 2:
            neu_gehalten = einsen + 1
        else:
            neu_gehalten = einsen
        for i in range(neu_gehalten):
            d[i] = 1
        gehalten = neu_gehalten
        if ist_starter:
            verdeckt = p[VERDECKT_WURF] == wurf + 1
        else:
            verdeckt = verdeckt_modus and wurf + 1 == grenze
    return (_schluessel(RANG[code, adh], wurf, position), verdeckt, code, adh, wurf)


@njit(cache=True)
def _haelfte(params, teilnehmer, starter, RANG, KLASSE, DECKEL):
    """Spielt eine Hälfte. teilnehmer: Spieler-Indizes in Sitzreihenfolge. Rückgabe: Verlierer."""
    n = teilnehmer.shape[0]
    deckel = np.zeros(n, dtype=np.int64)  # je Sitzplatz
    mitte = DECKEL_GESAMT
    start_platz = 0
    for i in range(n):
        if teilnehmer[i] == starter:
            start_platz = i
    reihen = np.zeros(n, dtype=np.int64)
    while True:
        # aktive Plätze ab Startplatz
        m = 0
        for j in range(n):
            platz = (start_platz + j) % n
            if mitte > 0 or deckel[platz] > 0:
                reihen[m] = platz
                m += 1
        grenze = 3
        verdeckt_modus = False
        min_offen = 0
        gibt_offen = False
        hoch_s, tief_s = -1, 1 << 60
        hoch_platz, tief_platz, hoch_deckel, hoch_aus = 0, 0, 0, False
        for pos in range(m):
            platz = reihen[pos]
            s, verdeckt, code, adh, wuerfe = _zug(params[teilnehmer[platz]], pos == 0, grenze, verdeckt_modus,
                                                  min_offen, gibt_offen, pos, RANG, KLASSE)
            if pos == 0:
                grenze = wuerfe
                verdeckt_modus = verdeckt
            if not verdeckt and (not gibt_offen or s < min_offen):
                min_offen = s
                gibt_offen = True
            if s > hoch_s:
                hoch_s, hoch_platz = s, platz
                hoch_deckel = DECKEL[code, adh]
                hoch_aus = KLASSE[code, adh] == 4
            if s < tief_s:
                tief_s, tief_platz = s, platz
        if hoch_aus:
            for j in range(n):
                deckel[j] = 0
            deckel[tief_platz] = DECKEL_GESAMT
            mitte = 0
        elif mitte > 0:
            menge = min(hoch_deckel, mitte)
            mitte -= menge
            deckel[tief_platz] += menge
        else:
            menge = min(hoch_deckel, deckel[hoch_platz])
            deckel[hoch_platz] -= menge
            deckel[tief_platz] += menge
        start_platz = tief_platz
        if deckel[tief_platz] == DECKEL_GESAMT:
            return teilnehmer[tief_platz]


@njit(cache=True)
def _spiel(params, starter, RANG, KLASSE, DECKEL):
    n = params.shape[0]
    alle = np.arange(n)
    v1 = _haelfte(params, alle, starter, RANG, KLASSE, DECKEL)
    v2 = _haelfte(params, alle, v1, RANG, KLASSE, DECKEL)
    if v1 == v2:
        return v1
    paar = np.empty(2, dtype=np.int64)
    paar[0], paar[1] = min(v1, v2), max(v1, v2)
    return _haelfte(params, paar, v2, RANG, KLASSE, DECKEL)


@njit(parallel=True, cache=True)
def _viele_spiele(params, anzahl, seed, RANG, KLASSE, DECKEL):
    n = params.shape[0]
    bloecke = 64
    verluste = np.zeros((bloecke, n), dtype=np.int64)
    pro_block = (anzahl + bloecke - 1) // bloecke
    for b in prange(bloecke):
        np.random.seed(seed * 1000003 + b)
        start = b * pro_block
        ende = min(anzahl, start + pro_block)
        for g in range(start, ende):
            starter = np.random.randint(0, n)
            verluste[b, _spiel(params, starter, RANG, KLASSE, DECKEL)] += 1
    return verluste.sum(axis=0)


def simuliere(params, anzahl: int, seed: int = 0) -> np.ndarray:
    """Spielt `anzahl` Spiele. params: (Spieler x N_PARAMS). Rückgabe: Verluste je Spieler."""
    params = np.ascontiguousarray(np.asarray(params, dtype=np.int64))
    return _viele_spiele(params, int(anzahl), int(seed), RANG, KLASSE, DECKEL)


def verlustquoten(params, anzahl: int, seed: int = 0):
    """Verlustquote je Spieler und 95%-Fehlerbalken."""
    v = simuliere(params, anzahl, seed)
    q = v / anzahl
    return q, 1.96 * np.sqrt(q * (1 - q) / anzahl)
