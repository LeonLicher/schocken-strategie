import unittest

import numpy as np

from schocken.analyse import (NEUTRAL_FOLGER, NEUTRAL_STARTER, Lage, aktion_text, folger_tabellen, optionen,
                              starter_tabellen, vergleiche_zug, zustand)
from schocken.loeser import _W_ID, wahl
from schocken.optimal import lade_loesung2
from schocken.wertung import bewerte


class TestAnalyse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = lade_loesung2()

    def test_beste_option_ist_die_entscheidung_der_loesung(self):
        lage = Lage("Finale", None, 0, 7, 6, "ich")
        t = starter_tabellen(self.s, lage)
        for wuerfel in [(4, 2, 1), (5, 1, 1), (6, 4, 3), (6, 6, 2)]:
            d, m, s = zustand(wuerfel, wuerfel)
            j, v = wahl(t.V, t.EV, *t.args, 2, d, m, s)
            self.assertEqual(optionen(t, 2, d, m, s)[0][0], aktion_text(d, m, s, j, v))

    def test_keine_abweichung_von_sich_selbst(self):
        t = starter_tabellen(self.s, NEUTRAL_STARTER)
        rec, To, Tv, erreicht = vergleiche_zug(t.V, t.EV, t.Uo, t.Uv, t.V, t.EV, t.Uo, t.Uv, 3, True, False)
        self.assertEqual(len(rec), 0)
        self.assertAlmostEqual(To.sum() + Tv.sum(), 1.0, places=9)

    def test_zug_enden_ergeben_eins_fuer_folger(self):
        ende = ("o", _W_ID[bewerte((6, 5, 3), False)], 2)
        f = folger_tabellen(self.s, NEUTRAL_FOLGER, ende)
        _, To, Tv, _ = vergleiche_zug(f.V, f.EV, f.Uo, f.Uv, f.V, f.EV, f.Uo, f.Uv, 2, False, False)
        self.assertAlmostEqual(To.sum() + Tv.sum(), 1.0, places=9)
        self.assertTrue(np.all(To[:, 3] == 0))


if __name__ == "__main__":
    unittest.main()
