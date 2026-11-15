"""Einfache Computer-Strategien als Vergleichsbasis."""

import random

from .engine import STOPP, Aktion, Sicht, Strategie, legale_aktionen

# Parameter-Indizes, identisch mit schocken/schnell.py
STARTER_KLASSE, VERDECKT_WURF, FOLGER_KLASSE, FOLGER_MARGE, DREHEN = range(5)
FAUSTREGEL_PARAMS = (1, 0, 1, 0, 1)


class Zufall(Strategie):
    """Wählt eine zufällige erlaubte Aktion. Nützlich zum Testen der Engine."""

    name = "Zufall"

    def __init__(self, seed=None):
        self.rng = random.Random(seed)

    def entscheide(self, sicht: Sicht) -> Aktion:
        return self.rng.choice(legale_aktionen(sicht))


class ParameterStrategie(Strategie):
    """Regelbasierte Strategie, beschrieben durch einen Parameter-Vektor (siehe schnell.py).

    Die gleiche Logik läuft im schnellen Simulator. So lässt sich der Simulator gegen die Engine prüfen.
    """

    name = "Parameter"

    def __init__(self, params=FAUSTREGEL_PARAMS, name=None):
        self.p = tuple(int(x) for x in params)
        if name:
            self.name = name

    def entscheide(self, sicht: Sicht) -> Aktion:
        p = self.p
        if sicht.phase == "vor_wurf":
            return Aktion(verdeckt=p[VERDECKT_WURF] == 1)
        if self._zufrieden(sicht):
            return STOPP
        a = self._weiter(sicht)
        if sicht.ist_starter:
            return Aktion(behalten=a.behalten, drehen=a.drehen, verdeckt=p[VERDECKT_WURF] == sicht.wurf_nr + 1)
        return a

    def _zufrieden(self, sicht: Sicht) -> bool:
        w = sicht.wertung
        if sicht.ist_starter:
            return w.klasse >= self.p[STARTER_KLASSE]
        offen = [e.vergleich for e in sicht.bisher if not e.verdeckt]
        if not offen:
            return w.klasse >= self.p[FOLGER_KLASSE]
        schlechtester = min(offen)
        mein = (w.rang, -sicht.wurf_nr, -sicht.position)
        return mein > schlechtester and w.rang >= schlechtester[0] + self.p[FOLGER_MARGE]

    def _weiter(self, sicht: Sicht) -> Aktion:
        einsen = min(sicht.wuerfel.count(1), 2)
        sechsen = sicht.neu.count(6)
        rest = sicht.grenze - sicht.wurf_nr
        drehen_ok = self.p[DREHEN] == 1
        if drehen_ok and einsen == 0 and sechsen >= 3 and rest >= 2:
            return Aktion(behalten=(), drehen=2)
        if drehen_ok and einsen < 2 and sechsen >= 2:
            return Aktion(behalten=(1,) * einsen, drehen=1)
        return Aktion(behalten=(1,) * einsen)


class Faustregel(ParameterStrategie):
    """Einfache Kneipen-Strategie.

    - Spielt immer offen.
    - Startspieler: hört ab einer Straße auf, sonst weiter.
    - Andere: hören auf, sobald sie besser als der schlechteste offene Wurf vor ihnen sind
      (ohne offenen Wurf vor ihnen: ab einer Straße).
    - Weiterwürfeln: Einsen behalten (max. 2), Sechsen drehen, wenn möglich.
    """

    name = "Faustregel"

    def __init__(self):
        super().__init__(FAUSTREGEL_PARAMS)


def aus_namen(name: str) -> Strategie:
    name = name.strip().lower()
    if name in ("zufall", "random"):
        return Zufall()
    if name in ("faustregel", "bot", "computer", "cpu"):
        return Faustregel()
    raise ValueError(f"Unbekannte Strategie: {name}")
