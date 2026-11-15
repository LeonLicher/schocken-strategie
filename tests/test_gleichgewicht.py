import time
import unittest

import numpy as np

from schocken import loeser
from schocken.gleichgewicht import N, _dist, _erw_paar, _praefix, runde2, runde3


def naiv_paar(x_sc, x_am, x_z, A, A_z, B, B_z, Vnext):
    out = np.zeros(N)
    for sa, aa, pa in zip(*A):
        for sb, ab, pb in zip(*B):
            sc = [(x_sc, x_am, x_z), (sa, aa, A_z), (sb, ab, B_z)]
            hoch = max(sc, key=lambda e: e[0])
            tief = min(sc, key=lambda e: e[0])
            out += pa * pb * Vnext[hoch[2], hoch[1], tief[2]]
    return out


def zufalls_vnext(rng):
    V = rng.random((N, 8, N, N))
    return V / V.sum(axis=3, keepdims=True)  # Vektoren summieren zu 1


class TestGleichgewicht(unittest.TestCase):
    def test_praefix_trick_wie_durchzaehlen(self):
        rng = np.random.default_rng(1)
        V = zufalls_vnext(rng)
        for art_a, xa, art_b, xb in [(1, 5, 1, 17), (0, 30, 1, 0), (1, 1, 0, 59), (1, 27, 1, 27)]:
            sa, aa, pa, na = _dist(art_a, xa, 2, 0)
            sb, ab, pb, nb = _dist(art_b, xb, 2, 1)
            cum, cum_am = _praefix(ab, pb, nb)
            for w in (0, 10, 33, 59):
                x_sc = loeser.RANG_W[w] * 100 + 10 * 2 + 7  # Score an Position 2, 1 Wurf
                out = np.zeros(N)
                _erw_paar(x_sc, loeser.DECK_W[w], 2, sa, aa, pa, na, 0, sb, nb, cum, cum_am, 1, V, out)
                erwartet = naiv_paar(x_sc, loeser.DECK_W[w], 2, (sa[:na], aa[:na], pa[:na]), 0,
                                     (sb[:nb], ab[:nb], pb[:nb]), 1, V)
                np.testing.assert_allclose(out, erwartet, rtol=1e-12, atol=1e-12)

    def test_runde_zu_zweit_wie_2_spieler_loeser(self):
        rng = np.random.default_rng(2)
        for _ in range(3):
            A, B = rng.random(8), rng.random(8)
            V = np.zeros((N, 8, N, N))
            for a in range(1, 8):
                V[1, a, 0] = [A[a], 1 - A[a], 0.0]  # Starter (Sitz 0) tief
                V[0, a, 1] = [B[a], 1 - B[a], 0.0]  # Folger (Sitz 1) tief
            z = np.array([0, 1, 0], dtype=np.int64)
            self.assertAlmostEqual(runde2(z, V)[0], loeser.runde2(A, B), places=10)

    def test_runde_zu_dritt_summe_eins(self):
        rng = np.random.default_rng(3)
        V = zufalls_vnext(rng)
        t = time.time()
        r = runde3(np.array([2, 0, 1], dtype=np.int64), V)
        self.dauer = time.time() - t
        self.assertAlmostEqual(r.sum(), 1.0, places=9)
        self.assertTrue(np.all(r >= 0))


if __name__ == "__main__":
    unittest.main()
