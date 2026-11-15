"""Spielablauf nach REGELN.md: Zug, Runde, Hälfte, Spiel.

Diese Engine ist auf Korrektheit und Lesbarkeit ausgelegt, nicht auf Tempo.
Strategien bekommen eine `Sicht` (nur öffentliche Information) und liefern eine `Aktion`.
"""

from dataclasses import dataclass, field, replace
from itertools import combinations
import random

from .wertung import DECKEL_GESAMT, Wertung, bewerte

MAX_WUERFE = 3


# --------------------------------------------------------------------------- Datentypen


@dataclass(frozen=True)
class Aktion:
    """Entscheidung eines Spielers.

    stopp:    Zug beenden, aktuelles Ergebnis offen stehen lassen.
    behalten: Würfelwerte, die herausgelegt bleiben (ohne gedrehte Einsen).
    drehen:   Anzahl Einsen, die aus Sechsen gedreht werden (2 Sechsen -> 1 Eins, 3 Sechsen -> 2 Einsen).
    verdeckt: Den nächsten Wurf stehen lassen (blind). Wählen darf das nur der Startspieler,
              bei allen anderen setzt die Engine den Wert selbst.
    """

    stopp: bool = False
    behalten: tuple = ()
    drehen: int = 0
    verdeckt: bool = False

    def normalisiert(self) -> "Aktion":
        if self.stopp:
            return STOPP
        return replace(self, behalten=tuple(sorted(self.behalten)))


STOPP = Aktion(stopp=True)


@dataclass(frozen=True)
class Ergebnis:
    """Endergebnis eines Zugs. Bei verdeckten Zügen sind `wuerfel`/`wertung` erst nach der Runde bekannt."""

    spieler: int
    position: int  # 0 = Startspieler der Runde
    wuerfe: int
    verdeckt: bool
    sichtbar: tuple  # Würfel, die alle sehen (bei verdeckt nur die herausgelegten)
    wuerfel: tuple | None
    aus_der_hand: bool | None
    wertung: Wertung | None

    @property
    def vergleich(self) -> tuple:
        """Größer = besser. Gleichstand: weniger Würfe gewinnt, dann der frühere Spieler."""
        return (self.wertung.rang, -self.wuerfe, -self.position)

    def oeffentlich(self) -> "Ergebnis":
        if not self.verdeckt:
            return self
        return replace(self, wuerfel=None, aus_der_hand=None, wertung=None)


@dataclass(frozen=True)
class Sicht:
    """Alles, was ein Spieler in einem Entscheidungsmoment weiß."""

    phase: str  # "vor_wurf" (nur Startspieler, vor dem 1. Wurf) oder "nach_wurf"
    spieler: int
    position: int
    ist_starter: bool
    grenze: int  # maximale Wurfzahl (Startspieler: 3)
    verdeckt_modus: bool  # Startspieler hat stehen lassen
    wurf_nr: int  # bisher geworfene Würfe
    wuerfel: tuple  # aktuelle drei Würfel (nach einem Wurf)
    neu: tuple  # im letzten Wurf geworfene Würfel
    bisher: tuple  # öffentliche Ergebnisse der Spieler vor mir (Ergebnis.oeffentlich())
    nach_mir: int  # Anzahl Spieler, die nach mir noch würfeln
    deckel: tuple  # (spieler, deckel) für alle Teilnehmer der Hälfte
    mitte: int
    haelfte: str  # "Hälfte 1", "Hälfte 2" oder "Finale"
    haelften_verlierer: tuple = ()  # Verlierer der bisherigen Hälften dieses Spiels

    @property
    def aus_der_hand(self) -> bool:
        return len(self.neu) == 3

    @property
    def wertung(self) -> Wertung:
        return bewerte(self.wuerfel, self.aus_der_hand)


class Strategie:
    """Basisklasse für Spieler (Mensch oder Computer)."""

    name = "Strategie"

    def entscheide(self, sicht: Sicht) -> Aktion:
        raise NotImplementedError


class RegelVerstoss(Exception):
    pass


# --------------------------------------------------------------------------- Regeln eines Zugs


def legale_aktionen(sicht: Sicht) -> list:
    """Alle erlaubten Aktionen in dieser Sicht (normalisiert)."""
    if sicht.phase == "vor_wurf":
        return [Aktion(), Aktion(verdeckt=True)] if sicht.ist_starter else [Aktion()]

    rest = sicht.grenze - sicht.wurf_nr
    if rest <= 0:
        return [STOPP]
    if sicht.ist_starter:
        verdeckt_optionen = (False, True)
    else:
        verdeckt_optionen = (sicht.verdeckt_modus and sicht.wurf_nr + 1 == sicht.grenze,)

    aktionen = [STOPP]
    sechsen = sicht.neu.count(6)
    for drehen in range(3):
        if drehen and (sechsen < drehen + 1 or rest < drehen):
            continue
        pool = list(sicht.wuerfel)
        for _ in range(drehen + 1 if drehen else 0):
            pool.remove(6)
        for anzahl in range(3 - drehen):  # behalten + gedreht <= 2: mindestens ein Würfel wird geworfen
            for behalten in sorted(set(combinations(sorted(pool), anzahl))):
                for verdeckt in verdeckt_optionen:
                    aktionen.append(Aktion(False, behalten, drehen, verdeckt))
    return aktionen


def _forciert_verdeckt(ist_starter, verdeckt_modus, grenze, naechster_wurf):
    return (not ist_starter) and verdeckt_modus and naechster_wurf == grenze


def spiele_zug(strategie, spieler, position, grenze, verdeckt_modus, kontext, rng) -> Ergebnis:
    """Ein kompletter Zug eines Spielers. `kontext` liefert die übrigen Sicht-Felder."""
    ist_starter = position == 0
    if ist_starter:
        grenze = MAX_WUERFE

    def sicht(phase, wurf_nr, wuerfel, neu):
        return Sicht(phase, spieler, position, ist_starter, grenze, verdeckt_modus,
                     wurf_nr, wuerfel, neu, **kontext)

    if ist_starter:
        a = _pruefe(strategie, sicht("vor_wurf", 0, (), ()), ist_starter=True)
        verdeckt = a.verdeckt
    else:
        verdeckt = _forciert_verdeckt(False, verdeckt_modus, grenze, 1)

    gehalten = ()
    wurf_nr = 0
    while True:
        neu = tuple(rng.randint(1, 6) for _ in range(3 - len(gehalten)))
        wurf_nr += 1
        wuerfel = gehalten + neu
        if verdeckt or wurf_nr >= grenze:
            break
        a = _pruefe(strategie, sicht("nach_wurf", wurf_nr, wuerfel, neu), ist_starter,
                    erzwungen=_forciert_verdeckt(ist_starter, verdeckt_modus, grenze, wurf_nr + 1))
        if a.stopp:
            break
        gehalten = a.behalten + (1,) * a.drehen
        verdeckt = a.verdeckt

    aus_der_hand = len(neu) == 3
    return Ergebnis(
        spieler=spieler, position=position, wuerfe=wurf_nr, verdeckt=verdeckt,
        sichtbar=gehalten if verdeckt else wuerfel, wuerfel=wuerfel,
        aus_der_hand=aus_der_hand, wertung=bewerte(wuerfel, aus_der_hand),
    )


def _pruefe(strategie, sicht, ist_starter, erzwungen=False) -> Aktion:
    a = strategie.entscheide(sicht).normalisiert()
    if not ist_starter and not a.stopp:
        a = replace(a, verdeckt=erzwungen)
    if a not in legale_aktionen(sicht):
        raise RegelVerstoss(f"{strategie.name}: unerlaubte Aktion {a} in {sicht}")
    return a


# --------------------------------------------------------------------------- Runde, Hälfte, Spiel


@dataclass(frozen=True)
class Regeln:
    """Platz für umschaltbare Hausregeln (derzeit keine)."""


@dataclass
class RundenErgebnis:
    ergebnisse: list
    hoch: Ergebnis
    tief: Ergebnis
    deckel_bewegt: int


def spiele_runde(reihenfolge, strategien, kontext_basis, rng) -> RundenErgebnis:
    ergebnisse = []
    grenze, verdeckt_modus = MAX_WUERFE, False
    for position, spieler in enumerate(reihenfolge):
        kontext = dict(kontext_basis,
                       bisher=tuple(e.oeffentlich() for e in ergebnisse),
                       nach_mir=len(reihenfolge) - position - 1)
        e = spiele_zug(strategien[spieler], spieler, position, grenze, verdeckt_modus, kontext, rng)
        if position == 0:
            grenze, verdeckt_modus = e.wuerfe, e.verdeckt
        ergebnisse.append(e)
    hoch = max(ergebnisse, key=lambda e: e.vergleich)
    tief = min(ergebnisse, key=lambda e: e.vergleich)
    return RundenErgebnis(ergebnisse, hoch, tief, 0)


@dataclass
class Haelfte:
    teilnehmer: list  # Sitzreihenfolge
    starter: int
    strategien: dict
    rng: random.Random
    name: str = "Hälfte"
    regeln: Regeln = field(default_factory=Regeln)
    log: object = None
    haelften_verlierer: tuple = ()
    deckel: dict = field(init=False)
    mitte: int = field(init=False, default=DECKEL_GESAMT)
    runden: int = field(init=False, default=0)

    def __post_init__(self):
        self.deckel = {p: 0 for p in self.teilnehmer}

    def aktive(self) -> list:
        if self.mitte > 0:
            return list(self.teilnehmer)
        return [p for p in self.teilnehmer if self.deckel[p] > 0]

    def reihenfolge(self) -> list:
        aktiv = self.aktive()
        i = aktiv.index(self.starter)
        return aktiv[i:] + aktiv[:i]

    def spiele(self) -> int:
        """Spielt die Hälfte zu Ende und gibt den Verlierer zurück."""
        while True:
            verlierer = self.spiele_runde()
            if verlierer is not None:
                return verlierer

    def spiele_runde(self):
        """Eine Runde. Gibt den Verlierer der Hälfte zurück, falls sie damit endet, sonst None."""
        kontext = dict(deckel=tuple(self.deckel.items()), mitte=self.mitte, haelfte=self.name,
                       haelften_verlierer=self.haelften_verlierer)
        r = spiele_runde(self.reihenfolge(), self.strategien, kontext, self.rng)
        self.runden += 1
        hoch, tief = r.hoch.spieler, r.tief.spieler
        vorher = self.deckel[tief]
        if r.hoch.wertung.ist_schock_aus:
            for p in self.teilnehmer:
                if p != tief:
                    self.deckel[tief] += self.deckel[p]
                    self.deckel[p] = 0
            self.deckel[tief] += self.mitte
            self.mitte = 0
        elif self.mitte > 0:
            # Solange die Mitte Deckel hat, kommt alles aus der Mitte (notfalls nur der Rest).
            menge = min(r.hoch.wertung.deckel, self.mitte)
            self.mitte -= menge
            self.deckel[tief] += menge
        else:
            menge = min(r.hoch.wertung.deckel, self.deckel[hoch])
            self.deckel[hoch] -= menge
            self.deckel[tief] += menge
        r.deckel_bewegt = self.deckel[tief] - vorher
        assert self.mitte + sum(self.deckel.values()) == DECKEL_GESAMT
        if self.log:
            self.log.runde(self, r)
        self.starter = tief
        return tief if self.deckel[tief] == DECKEL_GESAMT else None


@dataclass
class SpielErgebnis:
    verlierer: int
    haelften_verlierer: list  # [Hälfte 1, Hälfte 2] (+ Finale, falls gespielt)
    runden: int


def spiele_spiel(strategien: list, rng=None, regeln=None, log=None, starter=None) -> SpielErgebnis:
    """Ein komplettes Spiel: zwei Hälften, bei unterschiedlichen Verlierern ein Finale."""
    rng = rng or random.Random()
    regeln = regeln or Regeln()
    strat = dict(enumerate(strategien))
    alle = list(strat)
    starter = rng.randrange(len(alle)) if starter is None else starter

    def haelfte(teilnehmer, start, name, bisher=()):
        h = Haelfte(teilnehmer, start, strat, rng, name, regeln, log, tuple(bisher))
        if log:
            log.haelfte_start(h)
        v = h.spiele()
        if log:
            log.haelfte_ende(h, v)
        return v, h.runden

    v1, r1 = haelfte(alle, starter, "Hälfte 1")
    v2, r2 = haelfte(alle, v1, "Hälfte 2", [v1])
    if v1 == v2:
        return SpielErgebnis(v1, [v1, v2], r1 + r2)
    vf, rf = haelfte(sorted([v1, v2]), v2, "Finale", [v1, v2])
    return SpielErgebnis(vf, [v1, v2, vf], r1 + r2 + rf)
