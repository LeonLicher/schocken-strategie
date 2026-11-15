import random
import unittest
from unittest import mock

from schocken import engine
from schocken.bots import Faustregel, Zufall
from schocken.engine import (
    STOPP, Aktion, Ergebnis, Haelfte, RegelVerstoss, RundenErgebnis, Sicht, Strategie,
    legale_aktionen, spiele_runde, spiele_spiel, spiele_zug,
)
from schocken.wertung import EINFACH, GENERAL, SCHOCK, SCHOCK_AUS, STRASSE, alle_wertungen, bewerte


class SkriptWuerfel(random.Random):
    """Liefert vorgegebene Augenzahlen."""

    def __init__(self, augen):
        super().__init__(0)
        self.augen = list(augen)

    def randint(self, a, b):
        return self.augen.pop(0)


class Skript(Strategie):
    """Spielt vorgegebene Aktionen und merkt sich die Sichten."""

    name = "Skript"

    def __init__(self, *aktionen):
        self.aktionen = list(aktionen)
        self.sichten = []

    def entscheide(self, sicht):
        self.sichten.append(sicht)
        return self.aktionen.pop(0)


def sicht(**kw):
    basis = dict(phase="nach_wurf", spieler=0, position=0, ist_starter=True, grenze=3,
                 verdeckt_modus=False, wurf_nr=1, wuerfel=(1, 2, 3), neu=(1, 2, 3), bisher=(),
                 nach_mir=1, deckel=((0, 0), (1, 0)), mitte=13, haelfte="H")
    basis.update(kw)
    return Sicht(**basis)


KONTEXT = dict(bisher=(), nach_mir=0, deckel=(), mitte=13, haelfte="H")


class TestWertung(unittest.TestCase):
    def r(self, w, adh=False):
        return bewerte(w, adh).rang

    def test_reihenfolge_der_klassen(self):
        kette = [
            self.r((2, 2, 1)), self.r((3, 2, 1)), self.r((6, 6, 5)),
            self.r((1, 2, 3), True), self.r((4, 5, 6), True),
            self.r((2, 2, 2)), self.r((6, 6, 6)),
            self.r((1, 1, 2)), self.r((1, 1, 6)), self.r((1, 1, 1)),
        ]
        self.assertEqual(kette, sorted(kette))
        self.assertEqual(len(set(kette)), len(kette))

    def test_schlechtester_wurf_ist_221(self):
        self.assertEqual(alle_wertungen()[0], bewerte((2, 2, 1), False))

    def test_strasse_nur_aus_der_hand(self):
        self.assertEqual(bewerte((6, 5, 4), True).klasse, STRASSE)
        self.assertEqual(bewerte((6, 5, 4), False).klasse, EINFACH)
        self.assertLess(self.r((6, 5, 4)), self.r((6, 6, 5)))

    def test_general_und_schock_zusammengelegt(self):
        self.assertEqual(bewerte((3, 3, 3), False).klasse, GENERAL)
        self.assertEqual(bewerte((1, 1, 4), False).klasse, SCHOCK)
        self.assertEqual(bewerte((1, 1, 1), False).klasse, SCHOCK_AUS)

    def test_deckel(self):
        self.assertEqual(bewerte((6, 3, 2), True).deckel, 1)
        self.assertEqual(bewerte((2, 3, 4), True).deckel, 2)
        self.assertEqual(bewerte((5, 5, 5), False).deckel, 3)
        self.assertEqual(bewerte((1, 1, 5), False).deckel, 5)
        self.assertEqual(bewerte((1, 1, 1), True).deckel, 13)


class TestGleichstand(unittest.TestCase):
    def erg(self, pos, wuerfe):
        w = bewerte((6, 5, 3), False)
        return Ergebnis(pos, pos, wuerfe, False, (6, 5, 3), (6, 5, 3), False, w)

    def test_weniger_wuerfe_gewinnt(self):
        self.assertGreater(self.erg(2, 1).vergleich, self.erg(0, 2).vergleich)

    def test_dann_frueherer_spieler(self):
        self.assertGreater(self.erg(0, 2).vergleich, self.erg(1, 2).vergleich)


class TestLegaleAktionen(unittest.TestCase):
    def drehen(self, s):
        return {a.drehen for a in legale_aktionen(s) if not a.stopp}

    def test_drei_sechsen_im_ersten_wurf(self):
        self.assertEqual(self.drehen(sicht(wuerfel=(6, 6, 6), neu=(6, 6, 6))), {0, 1, 2})

    def test_zwei_einsen_drehen_braucht_zwei_restwuerfe(self):
        self.assertEqual(self.drehen(sicht(wurf_nr=2, wuerfel=(6, 6, 6), neu=(6, 6, 6))), {0, 1})
        s = sicht(ist_starter=False, position=1, grenze=2, wuerfel=(6, 6, 6), neu=(6, 6, 6))
        self.assertEqual(self.drehen(s), {0, 1})

    def test_nur_sechsen_aus_dem_letzten_wurf(self):
        self.assertEqual(self.drehen(sicht(wurf_nr=2, wuerfel=(6, 6, 3), neu=(3,))), {0})

    def test_mindestens_ein_wuerfel_wird_geworfen(self):
        for a in legale_aktionen(sicht(wuerfel=(6, 6, 1), neu=(6, 6, 1))):
            if not a.stopp:
                self.assertLessEqual(len(a.behalten) + a.drehen, 2)

    def test_letzter_wurf_nur_stopp(self):
        self.assertEqual(legale_aktionen(sicht(wurf_nr=3)), [STOPP])

    def test_verdeckt_erzwungen_fuer_andere(self):
        s = sicht(ist_starter=False, position=1, grenze=2, verdeckt_modus=True)
        weiter = [a for a in legale_aktionen(s) if not a.stopp]
        self.assertTrue(weiter and all(a.verdeckt for a in weiter))
        s = sicht(ist_starter=False, position=1, grenze=3, verdeckt_modus=True)
        self.assertTrue(all(not a.verdeckt for a in legale_aktionen(s)))

    def test_vor_wurf(self):
        self.assertEqual(len(legale_aktionen(sicht(phase="vor_wurf"))), 2)
        self.assertEqual(len(legale_aktionen(sicht(phase="vor_wurf", ist_starter=False))), 1)


class TestZug(unittest.TestCase):
    def test_starter_blind_im_ersten_wurf(self):
        e = spiele_zug(Skript(Aktion(verdeckt=True)), 0, 0, 3, False, KONTEXT, SkriptWuerfel([1, 1, 4]))
        self.assertTrue(e.verdeckt)
        self.assertEqual((e.wuerfe, e.sichtbar, e.wertung.name), (1, (), "Schock 4"))
        self.assertIsNone(e.oeffentlich().wertung)

    def test_sechsen_drehen(self):
        s = Skript(Aktion(), Aktion(behalten=(2,), drehen=1), STOPP)
        e = spiele_zug(s, 0, 0, 3, False, KONTEXT, SkriptWuerfel([6, 6, 2, 1]))
        self.assertEqual(sorted(e.wuerfel), [1, 1, 2])
        self.assertEqual((e.wuerfe, e.aus_der_hand), (2, False))

    def test_strasse_aus_der_hand_nach_neuwurf_aller(self):
        s = Skript(Aktion(), Aktion(behalten=()), STOPP)
        e = spiele_zug(s, 0, 0, 3, False, KONTEXT, SkriptWuerfel([6, 6, 2, 4, 5, 6]))
        self.assertEqual(e.wertung.klasse, STRASSE)

    def test_zusammengelegte_strasse(self):
        s = Skript(Aktion(), Aktion(behalten=(4, 5)), STOPP)
        e = spiele_zug(s, 0, 0, 3, False, KONTEXT, SkriptWuerfel([4, 5, 2, 6]))
        self.assertEqual(e.wertung.klasse, EINFACH)

    def test_unerlaubte_aktion(self):
        s = Skript(Aktion(), Aktion(behalten=(6, 6), drehen=1))
        with self.assertRaises(RegelVerstoss):
            spiele_zug(s, 0, 0, 3, False, KONTEXT, SkriptWuerfel([6, 6, 6]))


class TestRunde(unittest.TestCase):
    def test_grenze_und_verdeckt_modus(self):
        starter = Skript(Aktion(), Aktion(behalten=(1,), verdeckt=True))
        zweiter = Skript(Aktion(behalten=(1, 1)))
        dritter = Skript(STOPP)
        # Starter: 1 3 4, dann verdeckt 1 2 (=1 1 2). Zweiter: 1 1 5, dann verdeckt 3. Dritter: 6 6 5.
        w = SkriptWuerfel([1, 3, 4, 1, 2, 1, 1, 5, 3, 6, 6, 5])
        ctx = dict(deckel=(), mitte=13, haelfte="H")
        r = spiele_runde([0, 1, 2], {0: starter, 1: zweiter, 2: dritter}, ctx, w)
        a, b, c = r.ergebnisse
        self.assertEqual((a.wuerfe, a.verdeckt), (2, True))
        self.assertEqual((b.wuerfe, b.verdeckt, b.wertung.name), (2, True, "Schock 3"))
        self.assertEqual((c.wuerfe, c.verdeckt), (1, False))
        sicht_zweiter = zweiter.sichten[0]
        self.assertEqual((sicht_zweiter.grenze, sicht_zweiter.verdeckt_modus), (2, True))
        self.assertIsNone(sicht_zweiter.bisher[0].wertung)
        self.assertEqual(sicht_zweiter.bisher[0].sichtbar, (1,))
        self.assertEqual((r.hoch.spieler, r.tief.spieler), (1, 2))


def runde(hoch, tief, wurf):
    w = bewerte(wurf, False)
    e_h = Ergebnis(hoch, 0, 1, False, wurf, wurf, False, w)
    e_t = Ergebnis(tief, 1, 1, False, (2, 2, 1), (2, 2, 1), False, bewerte((2, 2, 1), False))
    return RundenErgebnis([e_h, e_t], e_h, e_t, 0)


class TestHaelfte(unittest.TestCase):
    def haelfte(self, n=3):
        return Haelfte(list(range(n)), 0, {}, random.Random(0))

    def spiele(self, h, r):
        with mock.patch.object(engine, "spiele_runde", return_value=r):
            return h.spiele_runde()

    def test_aus_der_mitte(self):
        h = self.haelfte()
        self.assertIsNone(self.spiele(h, runde(0, 1, (1, 1, 4))))
        self.assertEqual((h.deckel[1], h.mitte, h.starter), (4, 9, 1))

    def test_nur_rest_aus_der_mitte(self):
        h = self.haelfte()
        h.mitte, h.deckel = 2, {0: 5, 1: 6, 2: 0}
        self.spiele(h, runde(0, 2, (5, 5, 5)))
        self.assertEqual((h.deckel, h.mitte), ({0: 5, 1: 6, 2: 2}, 0))

    def test_vom_gewinner_wenn_mitte_leer(self):
        h = self.haelfte()
        h.mitte, h.deckel = 0, {0: 5, 1: 6, 2: 2}
        self.spiele(h, runde(0, 2, (5, 5, 5)))
        self.assertEqual(h.deckel, {0: 2, 1: 6, 2: 5})

    def test_gewinner_gibt_hoechstens_was_er_hat(self):
        h = self.haelfte()
        h.mitte, h.deckel = 0, {0: 1, 1: 6, 2: 6}
        self.spiele(h, runde(0, 2, (1, 1, 5)))
        self.assertEqual(h.deckel, {0: 0, 1: 6, 2: 7})

    def test_ohne_deckel_ausgeschieden(self):
        h = self.haelfte()
        h.mitte, h.deckel, h.starter = 0, {0: 0, 1: 6, 2: 7}, 2
        self.assertEqual(h.reihenfolge(), [2, 1])

    def test_schock_aus_beendet_haelfte(self):
        h = self.haelfte()
        h.mitte, h.deckel = 5, {0: 3, 1: 4, 2: 1}
        self.assertEqual(self.spiele(h, runde(0, 1, (1, 1, 1))), 1)
        self.assertEqual(h.deckel, {0: 0, 1: 13, 2: 0})

    def test_mitte_leer_meiste_deckel_beginnt(self):
        h = self.haelfte()
        h.mitte, h.deckel = 0, {0: 3, 1: 8, 2: 2}
        self.spiele(h, runde(1, 2, (5, 5, 5)))  # Spieler 2 verliert, bekommt 3 von Spieler 1
        self.assertEqual(h.deckel, {0: 3, 1: 5, 2: 5})
        self.assertEqual(h.starter, 2)  # Gleichstand 5:5 -> Verlierer beginnt

    def test_mitte_wird_leer_meiste_beginnt(self):
        h = self.haelfte()
        h.mitte, h.deckel = 2, {0: 6, 1: 5, 2: 0}
        self.spiele(h, runde(0, 2, (1, 1, 4)))  # Spieler 2 bekommt die letzten 2 aus der Mitte
        self.assertEqual((h.mitte, h.starter), (0, 0))

    def test_gleichstand_ab_verlierer_im_uhrzeigersinn(self):
        h = self.haelfte()
        h.mitte, h.deckel = 0, {0: 5, 1: 7, 2: 1}
        self.spiele(h, runde(1, 2, (1, 1, 2)))  # 1 gibt 2 an 2 -> 5:5:3, Gleichstand 0/1
        self.assertEqual(h.deckel, {0: 5, 1: 5, 2: 3})
        self.assertEqual(h.starter, 0)  # ab Verlierer 2 im Uhrzeigersinn: 0 vor 1

    def test_gleichstand_verlierer_nicht_dabei(self):
        h = self.haelfte()
        h.mitte, h.deckel = 0, {0: 7, 1: 1, 2: 5}
        self.spiele(h, runde(0, 1, (1, 1, 2)))  # 0 gibt 2 an 1 -> 5:3:5, Verlierer 1 -> nächster mit 5 ist 2
        self.assertEqual(h.deckel, {0: 5, 1: 3, 2: 5})
        self.assertEqual(h.starter, 2)

    def test_haelfte_endet_bei_13(self):
        h = self.haelfte(2)
        h.mitte, h.deckel = 0, {0: 2, 1: 11}
        self.assertEqual(self.spiele(h, runde(0, 1, (6, 6, 6))), 1)


class TestSpiel(unittest.TestCase):
    def test_viele_zufallsspiele(self):
        rng = random.Random(1)
        for i in range(400):
            n = 2 + i % 5
            strategien = [Zufall(i * 10 + k) if k % 2 else Faustregel() for k in range(n)]
            e = spiele_spiel(strategien, rng)
            self.assertIn(e.verlierer, range(n))
            if e.haelften_verlierer[0] == e.haelften_verlierer[1]:
                self.assertEqual(len(e.haelften_verlierer), 2)
            else:
                self.assertIn(e.verlierer, e.haelften_verlierer[:2])


if __name__ == "__main__":
    unittest.main()
