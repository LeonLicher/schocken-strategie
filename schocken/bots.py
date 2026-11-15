"""Einfache Computer-Strategien als Vergleichsbasis."""

import random

from .engine import STOPP, Aktion, Sicht, Strategie, legale_aktionen
from .wertung import STRASSE


class Zufall(Strategie):
    """Wählt eine zufällige erlaubte Aktion. Nützlich zum Testen der Engine."""

    name = "Zufall"

    def __init__(self, seed=None):
        self.rng = random.Random(seed)

    def entscheide(self, sicht: Sicht) -> Aktion:
        return self.rng.choice(legale_aktionen(sicht))


class Faustregel(Strategie):
    """Einfache Kneipen-Strategie.

    - Spielt immer offen.
    - Startspieler: hört ab einer Straße auf, sonst weiter.
    - Andere: hören auf, sobald sie besser als der schlechteste offene Wurf vor ihnen sind.
    - Weiterwürfeln: Einsen behalten (max. 2), Sechsen drehen, wenn möglich.
    """

    name = "Faustregel"

    def entscheide(self, sicht: Sicht) -> Aktion:
        if sicht.phase == "vor_wurf":
            return Aktion()
        if self._zufrieden(sicht):
            return STOPP
        return self._weiter(sicht)

    def _zufrieden(self, sicht: Sicht) -> bool:
        w = sicht.wertung
        if sicht.ist_starter:
            return w.klasse >= STRASSE
        offen = [e.vergleich for e in sicht.bisher if not e.verdeckt]
        if not offen:
            return w.klasse >= STRASSE
        mein = (w.rang, -sicht.wurf_nr, -sicht.position)
        return mein > min(offen)

    def _weiter(self, sicht: Sicht) -> Aktion:
        einsen = min(sicht.wuerfel.count(1), 2)
        sechsen = sicht.neu.count(6)
        rest = sicht.grenze - sicht.wurf_nr
        kandidaten = []
        if einsen == 0 and sechsen >= 3 and rest >= 2:
            kandidaten.append(Aktion(behalten=(), drehen=2))
        if einsen < 2 and sechsen >= 2:
            kandidaten.append(Aktion(behalten=(1,) * einsen, drehen=1))
        kandidaten.append(Aktion(behalten=(1,) * einsen))
        legal = legale_aktionen(sicht)
        for a in kandidaten:
            if a.normalisiert() in legal:
                return a
        return legal[1]


def aus_namen(name: str) -> Strategie:
    name = name.strip().lower()
    if name in ("zufall", "random"):
        return Zufall()
    if name in ("faustregel", "bot", "computer", "cpu"):
        return Faustregel()
    raise ValueError(f"Unbekannte Strategie: {name}")
