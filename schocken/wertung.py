"""Bewertung eines fertigen Wurfs (3 Würfel) nach REGELN.md."""

from dataclasses import dataclass
from itertools import combinations_with_replacement

EINFACH, STRASSE, GENERAL, SCHOCK, SCHOCK_AUS = range(5)

DECKEL_GESAMT = 13


@dataclass(frozen=True)
class Wertung:
    klasse: int
    schluessel: int  # Rang innerhalb der Klasse (höher = besser)
    deckel: int  # Strafdeckel, die dieser Wurf als Höchster verteilt (Schock Aus: alle)
    name: str

    @property
    def rang(self) -> int:
        """Gesamtrang, höher ist besser."""
        return self.klasse * 1000 + self.schluessel

    @property
    def ist_schock_aus(self) -> bool:
        return self.klasse == SCHOCK_AUS


def _berechne(wuerfel: tuple, aus_der_hand: bool) -> Wertung:
    w = sorted(wuerfel, reverse=True)
    a, b, c = w
    einsen = w.count(1)
    if einsen == 3:
        return Wertung(SCHOCK_AUS, 0, DECKEL_GESAMT, "Schock Aus")
    if einsen == 2:
        return Wertung(SCHOCK, a, a, f"Schock {a}")
    if a == b == c:
        return Wertung(GENERAL, a, 3, f"General {a}")
    if aus_der_hand and a - 1 == b and b - 1 == c:
        return Wertung(STRASSE, a, 2, f"Straße {c}-{b}-{a}")
    return Wertung(EINFACH, a * 100 + b * 10 + c, 1, f"{a}-{b}-{c}")


_TABELLE = {
    (wurf, adh): _berechne(wurf, adh)
    for wurf in combinations_with_replacement(range(1, 7), 3)
    for adh in (False, True)
}


def bewerte(wuerfel, aus_der_hand: bool) -> Wertung:
    """Bewertet drei Würfel. `aus_der_hand`: alle drei im letzten Wurf geworfen."""
    return _TABELLE[(tuple(sorted(wuerfel)), bool(aus_der_hand))]


def alle_wertungen():
    """Alle unterschiedlichen Wertungen, aufsteigend sortiert."""
    return sorted(set(_TABELLE.values()), key=lambda w: w.rang)
