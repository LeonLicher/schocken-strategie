import random
import unittest

import numpy as np

from schocken.bots import ParameterStrategie
from schocken.engine import spiele_spiel
from schocken.schnell import simuliere, verlustquoten

P = [(1, 0, 1, 0, 1), (5, 3, 2, 0, 0), (3, 2, 0, 200, 1)]


class TestSchnell(unittest.TestCase):
    def test_anzahl_und_reproduzierbar(self):
        a = simuliere(P, 5000, seed=3)
        self.assertEqual(a.sum(), 5000)
        self.assertTrue(np.array_equal(a, simuliere(P, 5000, seed=3)))

    def test_stimmt_mit_referenz_engine_ueberein(self):
        rng = random.Random(11)
        n_ref = 1500
        v = np.zeros(3)
        for _ in range(n_ref):
            v[spiele_spiel([ParameterStrategie(p) for p in P], rng).verlierer] += 1
        q_ref = v / n_ref
        q, _ = verlustquoten(P, 300_000, seed=5)
        se = np.sqrt(q_ref * (1 - q_ref) / n_ref)
        self.assertTrue(np.all(np.abs(q_ref - q) < 4.5 * se), (q_ref, q))


if __name__ == "__main__":
    unittest.main()
