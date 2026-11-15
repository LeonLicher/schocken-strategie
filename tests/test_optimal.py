import random
import unittest

from schocken.bots import Zufall
from schocken.engine import spiele_spiel
from schocken.optimal import Optimal2, lade_loesung2


class TestOptimal2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loesung = lade_loesung2()

    def test_spielt_nur_erlaubte_zuege(self):
        # Die Engine prüft jede Aktion; Zufall erzeugt viele ungewöhnliche (auch verdeckte) Situationen.
        rng = random.Random(4)
        for i in range(40):
            spieler = [Optimal2(self.loesung), Zufall(i)]
            if i % 2:
                spieler.reverse()
            spiele_spiel(spieler, rng)

    def test_symmetrie(self):
        s = self.loesung
        self.assertAlmostEqual(s.p_verlust(0) + s.p_verlust(1), 1.0, places=9)
        f = s.finale
        for mitte, d0 in [(13, 0), (5, 3), (0, 4)]:
            d1 = 13 - mitte - d0
            self.assertAlmostEqual(f.wert(mitte, d0, 0), 1 - f.wert(mitte, d1, 1), places=9)


if __name__ == "__main__":
    unittest.main()
