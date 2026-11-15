"""Terminal-Spiel: python -m schocken --spieler mensch,faustregel,faustregel"""

import argparse
import random

from .bots import aus_namen
from .engine import Sicht, Strategie, legale_aktionen, spiele_spiel


def _w(wuerfel) -> str:
    return " ".join(str(x) for x in sorted(wuerfel, reverse=True)) if wuerfel else "-"


def beschreibe(aktion, sicht: Sicht) -> str:
    if sicht.phase == "vor_wurf":
        return "Verdeckt würfeln (stehen lassen, blind für alle)" if aktion.verdeckt else "Offen würfeln"
    if aktion.stopp:
        return f"Fertig: {sicht.wertung.name} nach {sicht.wurf_nr} Wurf/Würfen"
    teile = [f"behalten: {_w(aktion.behalten)}"]
    if aktion.drehen:
        teile.append(f"{aktion.drehen + 1}x6 -> {aktion.drehen}x1 drehen")
    teile.append(f"{3 - len(aktion.behalten) - aktion.drehen} Würfel neu")
    if aktion.verdeckt:
        teile.append("VERDECKT")
    return ", ".join(teile)


class Namen:
    def __init__(self, strategien):
        self.namen = [f"{s.name} (P{i + 1})" for i, s in enumerate(strategien)]

    def __getitem__(self, i):
        return self.namen[i]


class Mensch(Strategie):
    name = "Mensch"

    def __init__(self, namen=None):
        self.namen = namen

    def entscheide(self, sicht: Sicht):
        n = self.namen
        print()
        print(f"--- {n[sicht.spieler]} am Zug ({sicht.haelfte}) ---")
        print("Deckel: " + ", ".join(f"{n[p]}={d}" for p, d in sicht.deckel) + f", Mitte={sicht.mitte}")
        for e in sicht.bisher:
            if e.verdeckt:
                print(f"  {n[e.spieler]}: VERDECKT nach {e.wuerfe} (sichtbar: {_w(e.sichtbar)})")
            else:
                print(f"  {n[e.spieler]}: {e.wertung.name} nach {e.wuerfe}")
        if sicht.ist_starter:
            print("  Du bist Startspieler.")
        else:
            modus = ", letzter Wurf verdeckt" if sicht.verdeckt_modus else ""
            print(f"  Maximal {sicht.grenze} Würfe{modus}. Nach dir noch {sicht.nach_mir} Spieler.")
        if sicht.phase == "nach_wurf":
            print(f"  Wurf {sicht.wurf_nr}: {_w(sicht.wuerfel)}  (neu: {_w(sicht.neu)})  = {sicht.wertung.name}")
        aktionen = legale_aktionen(sicht)
        for i, a in enumerate(aktionen):
            print(f"   [{i}] {beschreibe(a, sicht)}")
        while True:
            eingabe = input("Wahl [0]: ").strip()
            if eingabe == "":
                return aktionen[0]
            if eingabe.isdigit() and int(eingabe) < len(aktionen):
                return aktionen[int(eingabe)]
            print("Bitte eine Zahl aus der Liste eingeben.")


class Ausgabe:
    """Gibt den Spielverlauf im Terminal aus."""

    def __init__(self, namen):
        self.n = namen

    def haelfte_start(self, h):
        print(f"\n===== {h.name}: {', '.join(self.n[p] for p in h.teilnehmer)} =====")

    def runde(self, h, r):
        print(f"\n{h.name}, Runde {h.runden}:")
        for e in r.ergebnisse:
            zusatz = " (verdeckt)" if e.verdeckt else ""
            print(f"  {self.n[e.spieler]}: {_w(e.wuerfel)} = {e.wertung.name}, {e.wuerfe} Wurf/Würfe{zusatz}")
        print(f"  Hoch: {self.n[r.hoch.spieler]}, tief: {self.n[r.tief.spieler]} bekommt {r.deckel_bewegt} Deckel")
        print("  Stand: " + ", ".join(f"{self.n[p]}={d}" for p, d in h.deckel.items()) + f", Mitte={h.mitte}")

    def haelfte_ende(self, h, verlierer):
        print(f"\n>>> {self.n[verlierer]} verliert {h.name}.")


def main(argv=None):
    p = argparse.ArgumentParser(description="Schocken im Terminal")
    p.add_argument("--spieler", default="mensch,faustregel,faustregel",
                   help="Kommagetrennt: mensch, faustregel, zufall")
    p.add_argument("--seed", type=int, default=None)
    args = p.parse_args(argv)

    namen_liste = [s.strip() for s in args.spieler.split(",")]
    strategien = [Mensch() if s.lower() == "mensch" else aus_namen(s) for s in namen_liste]
    namen = Namen(strategien)
    for s in strategien:
        if isinstance(s, Mensch):
            s.namen = namen
    ergebnis = spiele_spiel(strategien, random.Random(args.seed), log=Ausgabe(namen))
    print(f"\n##### {namen[ergebnis.verlierer]} hat das Spiel verloren und zahlt die Runde! #####")


if __name__ == "__main__":
    main()
