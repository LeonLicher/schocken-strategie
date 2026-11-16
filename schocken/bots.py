"""Einfache Computer-Strategien als Vergleichsbasis."""

import random

from .engine import STOPP, Aktion, Sicht, Strategie, legale_aktionen
from .wertung import STRASSE, bewerte

# Parameter-Indizes, identisch mit schocken/schnell.py
STARTER_KLASSE, VERDECKT_WURF, FOLGER_KLASSE, FOLGER_MARGE, DREHEN = range(5)
FAUSTREGEL_PARAMS = (1, 3, 1, 0, 1)  # Startspieler wirft einen dritten Wurf verdeckt


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

    - Startspieler wirft einen dritten Wurf verdeckt (wie am Tisch üblich), sonst offen.
    - Startspieler: hört ab einer Straße auf, sonst weiter.
    - Andere: hören auf, sobald sie besser als der schlechteste offene Wurf vor ihnen sind
      (ohne offenen Wurf vor ihnen: ab einer Straße).
    - Weiterwürfeln: Einsen behalten (max. 2), Sechsen drehen, wenn möglich.
    """

    name = "Faustregel"

    def __init__(self):
        super().__init__(FAUSTREGEL_PARAMS)


def stammtisch_entscheidung(wurf_nr, wuerfel, neu, grenze, ist_starter):
    """Typische Stammtisch-Spielweise. Rückgabe: None = aufhören, sonst (behalten, gedrehte Einsen).

    - Sonderwurf (Straße aus der Hand, General, Schock, Schock Aus): stehen lassen.
    - Startspieler: ab dem 2. Wurf mit einer Eins aufhören; ohne Eins alle drei neu.
    - Alle anderen versuchen einen Schock zu bekommen: Einsen halten, Rest neu, bis der Schock da ist
      oder die Würfe aufgebraucht sind. Was die anderen haben, wird nicht beachtet.
    - Sechsen werden gedreht, wenn erlaubt und weniger als zwei Einsen liegen.
    - Der Startspieler wirft einen dritten Wurf verdeckt (wie am Tisch üblich), sonst wird offen geworfen.
    """
    if bewerte(wuerfel, len(neu) == 3).klasse >= STRASSE:
        return None
    einsen = min(list(wuerfel).count(1), 2)
    if ist_starter and wurf_nr >= 2 and einsen >= 1:
        return None
    rest = grenze - wurf_nr
    sechsen = list(neu).count(6)
    if einsen == 0 and sechsen >= 3 and rest >= 2:
        return (), 2
    if einsen < 2 and sechsen >= 2:
        return (1,) * einsen, 1
    return (1,) * einsen, 0


class Stammtisch(Strategie):
    """Spielt wie am Stammtisch üblich (siehe stammtisch_entscheidung)."""

    name = "Stammtisch"

    def entscheide(self, sicht: Sicht) -> Aktion:
        if sicht.phase == "vor_wurf":
            return Aktion()
        e = stammtisch_entscheidung(sicht.wurf_nr, sicht.wuerfel, sicht.neu, sicht.grenze, sicht.ist_starter)
        if e is None:
            return STOPP
        return Aktion(behalten=e[0], drehen=e[1], verdeckt=sicht.ist_starter and sicht.wurf_nr == 2)


def aus_namen(name: str) -> Strategie:
    name = name.strip().lower()
    if name in ("zufall", "random"):
        return Zufall()
    if name in ("faustregel", "bot", "computer", "cpu"):
        return Faustregel()
    if name == "stammtisch":
        return Stammtisch()
    if name == "konter":
        from .konter import Konter
        return Konter()
    if name in ("optimal", "optimal2"):
        from .optimal import Optimal2
        return Optimal2()
    raise ValueError(f"Unbekannte Strategie: {name}")
