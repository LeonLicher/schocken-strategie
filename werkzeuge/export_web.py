"""Exportiert die Lösungen für die Browser-Version (site/daten/*.json) und Testfälle (tests/js/faelle.json).

python werkzeuge/export_web.py
"""

import json
import os
import random
import sys
from pathlib import Path

os.environ.setdefault("NUMBA_NUM_THREADS", "1")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from schocken.bots import Stammtisch  # noqa: E402
from schocken.engine import legale_aktionen, spiele_spiel  # noqa: E402
from schocken.konter import F_FOLGER, S_START, Konter, datei as konter_datei, lade_konter  # noqa: E402
from schocken.optimal import Optimal2, lade_loesung2  # noqa: E402
from schocken.web.server import Berater  # noqa: E402

WURZEL = Path(__file__).resolve().parent.parent
DATEN = WURZEL / "site" / "daten"
FAELLE = WURZEL / "tests" / "js" / "faelle.json"


def r(x):
    return round(float(x), 12)


def haelfte_json(h):
    return {"t0": r(h.t0), "t1": r(h.t1), "X": [[m, d0, s, r(v)] for (m, d0, s), v in h.X.items()]}


def export_loesung2():
    s = lade_loesung2()
    return {"h1": haelfte_json(s.h1), "h2_0": haelfte_json(s.h2[0]), "h2_1": haelfte_json(s.h2[1]),
            "finale": haelfte_json(s.finale)}


def phase_name(p):
    return p if isinstance(p, str) else f"H2_{p[1]}"


def export_konter(n):
    L = lade_konter(n)
    return {"n": n,
            "V": {phase_name(p): [[m, *d, st, r(v)] for (m, d, st), v in tab.items()] for p, tab in L.V.items()},
            "S": [[r(x) for x in row] for row in S_START],
            "F": [[[r(x) for x in row] for row in F_FOLGER[L_]] for L_ in range(4)]}


# --------------------------------------------------------------------------- Testfälle


def sicht_json(s):
    def erg(e):
        return {"spieler": e.spieler, "position": e.position, "wuerfe": e.wuerfe, "verdeckt": e.verdeckt,
                "sichtbar": list(e.sichtbar), "wuerfel": list(e.wuerfel) if e.wuerfel else None,
                "ausDerHand": e.aus_der_hand, "wertung": {"name": e.wertung.name} if e.wertung else None}
    return {"phase": s.phase, "spieler": s.spieler, "position": s.position, "istStarter": s.ist_starter,
            "grenze": s.grenze, "verdecktModus": s.verdeckt_modus, "wurfNr": s.wurf_nr, "wuerfel": list(s.wuerfel),
            "neu": list(s.neu), "bisher": [erg(e) for e in s.bisher], "nachMir": s.nach_mir,
            "deckel": [list(x) for x in s.deckel], "mitte": s.mitte, "haelfte": s.haelfte,
            "haelftenVerlierer": list(s.haelften_verlierer)}


class Aufzeichner:
    """Spielt wie `bot`, merkt sich Sicht, Entscheidung und Werte aller Aktionen."""

    def __init__(self, bot, berater, faelle, art):
        self.bot, self.berater, self.faelle, self.art = bot, berater, faelle, art
        self.name = bot.name

    def entscheide(self, sicht):
        a = self.bot.entscheide(sicht).normalisiert()
        opts = self.berater.optionen(sicht)
        self.faelle.append({"art": self.art, "sicht": sicht_json(sicht),
                            "aktion": {"stopp": a.stopp, "behalten": list(a.behalten), "drehen": a.drehen,
                                       "verdeckt": a.verdeckt},
                            "optionen": [{"aktion": o["aktion"], "p": r(o["p"])} for o in opts],
                            "anzahl_legal": len(legale_aktionen(sicht))})
        return a


def testfaelle():
    rng = random.Random(7)
    faelle = []
    s2 = lade_loesung2()
    for i in range(6):
        b = Berater("optimal")
        spiele_spiel([Aufzeichner(Optimal2(s2), b, faelle, "optimal"), Optimal2(s2)], rng, starter=i % 2)
    for n in (2, 3):
        if not konter_datei(n).exists():
            continue
        b = Berater("konter")
        for i in range(4):
            spieler = [Aufzeichner(Konter(), b, faelle, f"konter{n}")] + [Stammtisch() for _ in range(n - 1)]
            spiele_spiel(spieler, rng, starter=i % n)
    return faelle


def main():
    DATEN.mkdir(parents=True, exist_ok=True)
    (DATEN / "loesung2.json").write_text(json.dumps(export_loesung2(), separators=(",", ":")), encoding="utf-8")
    for n in (2, 3, 4):
        if konter_datei(n).exists():
            (DATEN / f"konter{n}.json").write_text(json.dumps(export_konter(n), separators=(",", ":")), encoding="utf-8")
    for f in sorted(DATEN.glob("*.json")):
        print(f"{f.name}: {f.stat().st_size // 1024} KB")
    FAELLE.parent.mkdir(parents=True, exist_ok=True)
    faelle = testfaelle()
    FAELLE.write_text(json.dumps(faelle, separators=(",", ":")), encoding="utf-8")
    print(f"{len(faelle)} Testfälle -> {FAELLE}")


if __name__ == "__main__":
    main()
