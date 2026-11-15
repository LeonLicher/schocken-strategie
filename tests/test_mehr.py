import unittest

import numpy as np

from schocken.konter import F_FOLGER, S_START
from schocken.mehr import ausgang_verteilung
from schocken.loeser import DECK_W, RANG_W, W


def naiv(n, D):
    """Durchzählen aller Kombinationen (nur für kleine Tests)."""
    traeger = []
    for pos in range(n):
        traeger.append([(RANG_W[w] * 100 + (3 - k) * 10 + (9 - pos), DECK_W[w], D[pos, w, k])
                        for k in range(1, 4) for w in range(W) if D[pos, w, k] > 0])
    P = np.zeros((n, 8, n))

    def rek(pos, gewaehlt, p):
        if pos == n:
            h = max(range(n), key=lambda i: gewaehlt[i][0])
            t = min(range(n), key=lambda i: gewaehlt[i][0])
            P[h, gewaehlt[h][1], t] += p
            return
        for e in traeger[pos]:
            rek(pos + 1, gewaehlt + [e], p * e[2])
    rek(0, [], 1.0)
    return P


class TestAusgangVerteilung(unittest.TestCase):
    def test_wie_durchzaehlen(self):
        rng = np.random.default_rng(5)
        for n in (2, 3, 4):
            D = np.zeros((n, W, 4))
            for pos in range(n):
                w = rng.choice(W, size=6, replace=False)
                k = rng.integers(1, 4, size=6)
                D[pos, w, k] = rng.random(6)
                D[pos] /= D[pos].sum()
            np.testing.assert_allclose(ausgang_verteilung(n, D), naiv(n, D), atol=1e-12)

    def test_summe_eins_bei_sechs(self):
        D = np.zeros((6, W, 4))
        D[0, :, 3] = S_START[:, 3] / S_START[:, 3].sum()
        for pos in range(1, 6):
            D[pos] = F_FOLGER[3]
        self.assertAlmostEqual(ausgang_verteilung(6, D).sum(), 1.0, places=10)


if __name__ == "__main__":
    unittest.main()
