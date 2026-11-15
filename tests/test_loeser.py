import unittest
from functools import lru_cache
from itertools import product

import numpy as np

from schocken.engine import Sicht, legale_aktionen
from schocken.loeser import H_ID, NH, W, _W_ID, runde2, zug_dp
from schocken.wertung import bewerte


def brute_force(U_offen, U_verdeckt, grenze, ist_starter, verdeckt_modus):
    """Expectimax direkt über engine.legale_aktionen (unabhängig von den Löser-Tabellen)."""
    if ist_starter:
        grenze = 3

    def sicht(phase, k, wuerfel, neu):
        return Sicht(phase, 0, 0 if ist_starter else 1, ist_starter, grenze, verdeckt_modus, k,
                     wuerfel, neu, (), 0, (), 13, "H")

    def wurf(k, gehalten):
        r = 3 - len(gehalten)
        return sum(nach_wurf(k, tuple(sorted(gehalten + w)), tuple(sorted(w))) for w in product(range(1, 7), repeat=r)) / 6 ** r

    @lru_cache(maxsize=None)
    def nach_wurf(k, wuerfel, neu):
        best = -1e9
        for a in legale_aktionen(sicht("nach_wurf", k, wuerfel, neu)):
            if a.stopp:
                v = U_offen[_W_ID[bewerte(wuerfel, len(neu) == 3)], k]
            else:
                gehalten = tuple(sorted(a.behalten + (1,) * a.drehen))
                v = U_verdeckt[H_ID[gehalten], k + 1] if a.verdeckt else wurf(k + 1, gehalten)
            best = max(best, v)
        return best

    werte = []
    for a in legale_aktionen(sicht("vor_wurf", 0, (), ())):
        if ist_starter:
            werte.append(U_verdeckt[0, 1] if a.verdeckt else wurf(1, ()))
        else:
            werte.append(U_verdeckt[0, 1] if verdeckt_modus and grenze == 1 else wurf(1, ()))
    return max(werte)


class TestZugDP(unittest.TestCase):
    def test_gegen_brute_force(self):
        rng = np.random.default_rng(0)
        faelle = [(3, True, False), (3, False, False), (2, False, False), (1, False, False),
                  (3, False, True), (2, False, True), (1, False, True)]
        for grenze, starter, vm in faelle:
            with self.subTest(grenze=grenze, starter=starter, verdeckt_modus=vm):
                U_offen = rng.random((W, 4))
                U_verdeckt = rng.random((NH, 4))
                erwartet = brute_force(U_offen, U_verdeckt, grenze, starter, vm)
                wert, _, _ = zug_dp(U_offen, U_verdeckt, 3 if starter else grenze, starter, vm)
                self.assertAlmostEqual(wert, erwartet, places=10)

    def test_wahrscheinlichkeit_schock_aus(self):
        # Maximale Chance auf Schock Aus mit 3 offenen Würfen (ohne Verdecken sinnvoll)
        U_offen = np.zeros((W, 4))
        U_offen[_W_ID[bewerte((1, 1, 1), False)], 1:] = 1.0
        wert, _, _ = zug_dp(U_offen, np.zeros((NH, 4)), 3, False, False)
        self.assertGreater(wert, 1 / 216)
        self.assertLess(wert, 0.2)


class TestRunde2(unittest.TestCase):
    def test_extremfaelle(self):
        eins, null = np.ones(8), np.zeros(8)
        self.assertAlmostEqual(runde2(eins, eins), 1.0)
        self.assertAlmostEqual(runde2(null, null), 0.0)
        # Starter verliert nur, wenn er tief ist: Wert = P(Starter tief) liegt echt zwischen 0 und 1
        p = runde2(eins, null)
        self.assertTrue(0.0 < p < 1.0)


if __name__ == "__main__":
    unittest.main()
