import random
import unittest
from collections import Counter

import numpy as np

from schocken.bots import Stammtisch
from schocken.engine import spiele_zug
from schocken.konter import F_FOLGER, S_START
from schocken.loeser import _W_ID

KONTEXT = dict(bisher=(), nach_mir=1, deckel=(), mitte=13, haelfte="Hälfte 1")


class TestStammtischVerteilung(unittest.TestCase):
    def test_summe_eins(self):
        self.assertAlmostEqual(S_START.sum(), 1.0, places=12)
        for L in (1, 2, 3):
            self.assertAlmostEqual(F_FOLGER[L].sum(), 1.0, places=12)
            self.assertEqual(F_FOLGER[L][:, L + 1:].sum(), 0.0)

    def vergleiche(self, P, position, grenze):
        rng = random.Random(1)
        n = 30000
        zaehler = Counter()
        for _ in range(n):
            e = spiele_zug(Stammtisch(), 0, position, grenze, False, KONTEXT, rng)
            zaehler[(_W_ID[e.wertung], e.wuerfe)] += 1
        # Wurfzahl-Verteilung und die häufigsten Ergebnisse müssen passen
        for k in range(1, 4):
            beob = sum(c for (w, kk), c in zaehler.items() if kk == k) / n
            erw = P[:, k].sum()
            self.assertLess(abs(beob - erw), 4.5 * np.sqrt(erw * (1 - erw) / n) + 1e-9, (k, beob, erw))
        for (w, k), c in zaehler.most_common(8):
            erw = P[w, k]
            self.assertLess(abs(c / n - erw), 4.5 * np.sqrt(erw * (1 - erw) / n), (w, k, c / n, erw))

    def test_starter_passt_zur_engine(self):
        self.vergleiche(S_START, 0, 3)

    def test_folger_passt_zur_engine(self):
        self.vergleiche(F_FOLGER[2], 1, 2)


if __name__ == "__main__":
    unittest.main()
