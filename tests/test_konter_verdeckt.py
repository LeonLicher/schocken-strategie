"""Rundenkerne von Konter, wenn der Stammtisch-Startspieler verdeckt zum dritten Mal wirft: der schnelle
Kern muss dasselbe liefern wie der Weg des Bots (jede Vorgeschichte einzeln mit folger_bewertung_allgemein)."""

import unittest

import numpy as np

from schocken.konter import (F3_VERDECKT, F_FOLGER, S_OFFEN, S_START, S_VERDECKT, folger_bewertung_allgemein,
                             wert_runde)
from schocken.loeser import NH, P_VERDECKT, W, zug_dp


def bot_weg(n, seats, p, Vn):
    """Wert der Runde für mich an Position p (1 oder n-1), Vorgeschichten einzeln aufgezählt."""
    tot = 0.0

    def mein_wert(D_vor, k1, vm):
        Uo, Uv = folger_bewertung_allgemein(n, seats, p, D_vor, k1, F_FOLGER, Vn, vm)
        return -zug_dp(Uo, Uv, k1, False, vm)[0]

    starter = [(S_OFFEN[w, k], k, False, w) for k in (1, 2) for w in range(W) if S_OFFEN[w, k] > 0]
    starter += [(S_VERDECKT[h], 3, True, h) for h in range(NH) if S_VERDECKT[h] > 0]
    for p1, k1, vm, x in starter:
        D0 = np.zeros((W, 4))
        if vm:
            D0[:, 3] = P_VERDECKT[x]
        else:
            D0[x, k1] = 1.0
        if p == 1:
            D_vor = np.zeros((3, W, 4))
            D_vor[0] = D0
            tot += p1 * mein_wert(D_vor, k1, vm)
            continue
        # p == 2 (n = 3): Mittlerer endet offen (k2 < k1 oder ohne Verdeckt-Modus) oder verdeckt im dritten
        mitte = [(F_FOLGER[k1][w, k], w, k, False) for k in range(1, k1 + 1) for w in range(W)
                 if F_FOLGER[k1][w, k] > 0 and not (vm and k == 3)]
        if vm:
            mitte += [(F3_VERDECKT[h], h, 3, True) for h in range(NH) if F3_VERDECKT[h] > 0]
        for p2, x2, k2, v2 in mitte:
            D_vor = np.zeros((3, W, 4))
            D_vor[0] = D0
            if v2:
                D_vor[1, :, 3] = P_VERDECKT[x2]
            else:
                D_vor[1, x2, k2] = 1.0
            tot += p1 * p2 * mein_wert(D_vor, k1, vm)
    return tot


class TestKonterVerdeckt(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(7)
        self.Vn = rng.random((3, 8, 3))
        self.seats = np.array([1, 2, 0], dtype=np.int64)

    def test_verteilungen(self):
        self.assertAlmostEqual(S_OFFEN.sum() + S_VERDECKT.sum(), 1.0, places=12)
        np.testing.assert_allclose(S_VERDECKT @ P_VERDECKT, S_START[:, 3], atol=1e-15)

    def test_zwei_spieler_letzter(self):
        seats = np.array([1, 0, 0], dtype=np.int64)
        self.assertAlmostEqual(wert_runde(2, seats, 1)(self.Vn), bot_weg(2, seats, 1, self.Vn), places=12)

    def test_drei_spieler_zweiter(self):
        self.assertAlmostEqual(wert_runde(3, self.seats, 1)(self.Vn), bot_weg(3, self.seats, 1, self.Vn), places=12)

    def test_drei_spieler_letzter(self):
        self.assertAlmostEqual(wert_runde(3, self.seats, 2)(self.Vn), bot_weg(3, self.seats, 2, self.Vn), places=12)


if __name__ == "__main__":
    unittest.main()
