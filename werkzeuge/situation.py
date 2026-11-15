"""Was ist in dieser Situation am besten? (Schocken zu zweit, exakte Lösung)

Beispiele:
  # Finale, ich beginne, Mitte leer, ich 7 : Gegner 6, nach Wurf 2 – alle Würfe ohne Angabe:
  python werkzeuge/situation.py --haelfte finale --mitte 0 --ich 7 --gegner 6 --start ich --wurf 2

  # dieselbe Lage, konkreter Wurf 6-4-3 (alle drei neu geworfen):
  python werkzeuge/situation.py --haelfte finale --mitte 0 --ich 7 --gegner 6 --start ich --wurf 2 --wuerfel 643

  # ich bin Folgespieler, Gegner hat 6-5-3 nach 2 Würfen offen:
  python werkzeuge/situation.py --mitte 10 --ich 3 --gegner 0 --start gegner --gegner-ergebnis 653 --gegner-wuerfe 2 --wurf 1
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from schocken.analyse import (NEUTRAL_FOLGER, NEUTRAL_STARTER, Lage, ende_text, folger_tabellen,  # noqa: E402
                              optionen, starter_tabellen, zustand)
from schocken.loeser import D_LISTE, H_ID, _W_ID, wahl  # noqa: E402
from schocken.optimal import lade_loesung2  # noqa: E402
from schocken.wertung import bewerte  # noqa: E402

HAELFTEN = {"1": "Hälfte 1", "2": "Hälfte 2", "finale": "Finale"}


def ziffern(text):
    return tuple(int(c) for c in text if c.isdigit())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--haelfte", choices=HAELFTEN, default="finale")
    ap.add_argument("--h1", choices=("ich", "gegner"), help="Wer Hälfte 1 verloren hat (nur bei Hälfte 2)")
    ap.add_argument("--mitte", type=int, required=True)
    ap.add_argument("--ich", type=int, required=True)
    ap.add_argument("--gegner", type=int, required=True)
    ap.add_argument("--start", choices=("ich", "gegner"), required=True)
    ap.add_argument("--wurf", type=int, required=True, help="Anzahl bisheriger Würfe (0 = vor dem ersten)")
    ap.add_argument("--wuerfel", help="Aktuelle drei Würfel, z. B. 643")
    ap.add_argument("--neu", help="Davon im letzten Wurf neu geworfen (Standard: alle drei)")
    ap.add_argument("--gegner-ergebnis", help="Offenes Ergebnis des startenden Gegners, z. B. 653")
    ap.add_argument("--gegner-hand", action="store_true", help="Gegner-Ergebnis fiel aus der Hand (für Straßen)")
    ap.add_argument("--gegner-verdeckt", help="Gegner hat verdeckt; sichtbare Würfel, z. B. 1 oder 11 (leer: '')")
    ap.add_argument("--gegner-wuerfe", type=int, help="Wurfzahl des Gegners (= meine Grenze)")
    a = ap.parse_args()

    s = lade_loesung2()
    lage = Lage(HAELFTEN[a.haelfte], a.h1 if a.haelfte == "2" else None, a.mitte, a.ich, a.gegner, a.start)
    if a.start == "ich":
        t, basis = starter_tabellen(s, lage), starter_tabellen(s, NEUTRAL_STARTER)
    else:
        if a.gegner_wuerfe is None or (a.gegner_ergebnis is None and a.gegner_verdeckt is None):
            ap.error("Als Folgespieler bitte --gegner-wuerfe und --gegner-ergebnis oder --gegner-verdeckt angeben.")
        if a.gegner_verdeckt is not None:
            ende = ("v", H_ID[tuple(sorted(ziffern(a.gegner_verdeckt)))], a.gegner_wuerfe)
        else:
            ende = ("o", _W_ID[bewerte(ziffern(a.gegner_ergebnis), a.gegner_hand)], a.gegner_wuerfe)
        t, basis = folger_tabellen(s, lage, ende), folger_tabellen(s, NEUTRAL_FOLGER, ende)
        print(ende_text(ende))
    print(lage.text())

    if a.wurf == 0:
        if not t.darf:
            ap.error("Vor dem ersten Wurf entscheidet nur der Startspieler.")
        o, v = t.p_verlust(t.EV[1, 0]), t.p_verlust(t.Uv[0, 1])
        print(f"  offen beginnen:    P(ich verliere das Spiel) = {o:.4f}")
        print(f"  verdeckt beginnen: P(ich verliere das Spiel) = {v:.4f}")
        return

    if a.wuerfel:
        wuerfel = ziffern(a.wuerfel)
        neu = ziffern(a.neu) if a.neu else wuerfel
        d, m, sx = zustand(wuerfel, neu)
        jb, vb = wahl(basis.V, basis.EV, *basis.args, a.wurf, d, m, sx)
        from schocken.analyse import aktion_text
        print(f"\nNach Wurf {a.wurf}: {'-'.join(map(str, sorted(wuerfel, reverse=True)))} "
              f"(neu: {len(neu)} Würfel). Basis (Spielbeginn) würde: {aktion_text(d, m, sx, jb, vb)}")
        for i, (text, p) in enumerate(optionen(t, a.wurf, d, m, sx)):
            print(f"  {'BESTE ' if i == 0 else '      '}{text:32s} P(ich verliere das Spiel) = {p:.4f}")
        return

    # Übersicht: alle Würfe, bei denen alle drei Würfel neu geworfen wurden
    print(f"\nNach Wurf {a.wurf}, alle drei Würfel neu geworfen. Beste Entscheidung (Basis = Spielbeginn):")
    for d, wurf in enumerate(D_LISTE):
        m, sx = 3, wurf.count(6)
        opts = optionen(t, a.wurf, d, m, sx)
        from schocken.analyse import aktion_text
        jb, vb = wahl(basis.V, basis.EV, *basis.args, a.wurf, d, m, sx)
        basis_text = aktion_text(d, m, sx, jb, vb)
        best, p_best = opts[0]
        p_basis = dict(opts).get(basis_text, p_best)
        markierung = f"   <- ANDERS als Basis ({basis_text}: {p_basis:.4f}, +{(p_basis - p_best) * 100:.2f} %-Pkt.)" \
            if basis_text != best else ""
        print(f"  {'-'.join(map(str, sorted(wurf, reverse=True)))}: {best:28s} {p_best:.4f}{markierung}")


if __name__ == "__main__":
    main()
